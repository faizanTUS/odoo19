# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
import ast
import json
import logging

from odoo import api, models, tools, SUPERUSER_ID

_logger = logging.getLogger(__name__)

# Models that stay writable when global read-only is on (minimal system behavior).
_GLOBAL_RO_WHITELIST = frozenset(
    {
        "advanced.access.policy",
        "advanced.access.policy.model.line",
        "advanced.access.policy.field.line",
        "advanced.access.policy.menu.line",
        "advanced.access.policy.button.line",
        "advanced.access.policy.tab.line",
        "advanced.access.audit.log",
        "mail.message",
        "mail.notification",
        "bus.bus",
        "bus.presence",
        "res.users", # Required for login_date updates
        "res.users.log", # Required for login tracking
        "ir.attachment",
        "ir.logging",
    }
)


def _aac_merge_model_ui(model_rules):
    """Per-model flags for UI (session). Any line denying an operation clears that flag.
    Duplicate also requires create (copy creates a new record)."""
    by_model = {}
    for r in model_rules:
        m = r["model"]
        cur = by_model.setdefault(
            m,
            {
                "create": True,
                "write": True,
                "unlink": True,
                "export": True,
                "duplicate": True,
                "import": True,
                "archive": True,
            },
        )
        if not r["allow_create"]:
            cur["create"] = False
        if not r["allow_write"]:
            cur["write"] = False
        if not r["allow_unlink"]:
            cur["unlink"] = False
        if not r["allow_export"]:
            cur["export"] = False
        if not r["allow_duplicate"]:
            cur["duplicate"] = False
        if not r["allow_import"]:
            cur["import"] = False
        if not r["allow_archive"]:
            cur["archive"] = False
    for cur in by_model.values():
        cur["duplicate"] = bool(cur["duplicate"] and cur["create"])
    return by_model


def _aac_binding_action_ids_matching(env, model_name, mode):
    """Return ``ir.actions.actions`` ids bound to ``model_name`` for cancel- or email-style sidebar entries."""
    im = env["ir.model"].sudo().search([("model", "=", model_name)], limit=1)
    if not im:
        return set()
    acts = env["ir.actions.actions"].sudo().search([("binding_model_id", "=", im.id)])
    found = set()
    for act in acts:
        n = (act.name or "").strip().lower()
        if not n:
            continue
        if mode == "cancel":
            if n == "cancel" or n.startswith("cancel ") or n.endswith(" cancel"):
                found.add(act.id)
        elif mode == "email":
            if "email" in n or "e-mail" in n:
                found.add(act.id)
    return found


def _parse_domain(text):
    if not text or not str(text).strip():
        return []
    try:
        value = ast.literal_eval(str(text).strip())
    except (ValueError, SyntaxError):
        return []
    if not isinstance(value, (list, tuple)):
        return []
    return list(value)


class AdvancedAccessService(models.AbstractModel):
    _name = "advanced.access.service"
    _description = "Advanced access rule cache and helpers"

    @api.model
    @tools.ormcache("self.env.uid")
    def _rules_payload_json(self):
        """Frozen JSON string of effective rules for current user (for client + server)."""
        uid = self.env.uid
        if not uid:
            return json.dumps({"empty": True})
        user = self.env["res.users"].browse(uid)
        su = user.sudo()
        # User #1 (Superuser) is ALWAYS bypassed for safety.
        # AAC-Managers are also bypassed.
        if user._is_superuser() or user.has_group("advanced_access_control.group_advanced_access_manager"):
            return json.dumps({"empty": True})

        policies = self.env["advanced.access.policy"].sudo().search(
            [
                ("active", "=", True),
                "|",
                ("user_ids", "in", [uid]),
                ("group_ids", "in", user.groups_id.ids),
            ]
        )
        if not policies:
            return json.dumps({"empty": True})

        hidden_menus = set()
        buttons_by_model = {}
        tabs_by_model = {}
        fields_by_model = {}
        model_rules = []
        hidden_reports_by_model = {}
        hidden_sidebar_action_ids_by_model = {}

        for pol in policies:
            for line in pol.menu_line_ids:
                hidden_menus.add(line.menu_id.id)
            for line in pol.button_line_ids:
                buttons_by_model.setdefault(line.model_name, set()).add(line.button_name)
            for line in pol.tab_line_ids:
                tabs_by_model.setdefault(line.model_name, set()).add(line.page_string)
            for line in pol.field_line_ids:
                fields_by_model.setdefault(line.model_name, []).append(
                    {
                        "field": line.field_name,
                        "modifier": line.modifier,
                        "expr": line.apply_condition or "",
                    }
                )
            for line in pol.model_line_ids:
                model_rules.append(
                    {
                        "policy_id": pol.id,
                        "model": line.model_name,
                        "allow_read": line.allow_read,
                        "allow_create": line.allow_create,
                        "allow_write": line.allow_write,
                        "allow_unlink": line.allow_unlink,
                        "allow_export": line.allow_export,
                        "allow_duplicate": line.allow_duplicate,
                        "allow_import": line.allow_import,
                        "allow_archive": line.allow_archive,
                        "allow_sidebar_cancel": line.allow_sidebar_cancel,
                        "allow_sidebar_send_email": line.allow_sidebar_send_email,
                        "domain": _parse_domain(line.record_domain),
                    }
                )
                if line.hidden_report_ids:
                    hidden_reports_by_model.setdefault(line.model_name, set()).update(
                        line.hidden_report_ids.ids
                    )
                sid = set()
                if not line.allow_sidebar_cancel:
                    sid |= _aac_binding_action_ids_matching(
                        self.env, line.model_name, "cancel"
                    )
                if not line.allow_sidebar_send_email:
                    sid |= _aac_binding_action_ids_matching(
                        self.env, line.model_name, "email"
                    )
                if sid:
                    hidden_sidebar_action_ids_by_model.setdefault(
                        line.model_name, set()
                    ).update(sid)
                if line.hidden_sidebar_action_ids:
                    hidden_sidebar_action_ids_by_model.setdefault(
                        line.model_name, set()
                    ).update(line.hidden_sidebar_action_ids.ids)

        model_ui = _aac_merge_model_ui(model_rules)

        payload = {
            "empty": False,
            "global_readonly": any(p.global_readonly for p in policies),
            "hide_chatter": any(p.hide_chatter for p in policies),
            "disable_debug": any(p.disable_debug for p in policies),
            "audit": any(p.enable_audit for p in policies),
            "global_disable_import": any(p.global_disable_import for p in policies),
            "global_disable_export": any(p.global_disable_export for p in policies),
            "global_disable_archive": any(p.global_disable_archive for p in policies),
            "policy_ids": policies.ids,
            "hidden_menu_ids": sorted(hidden_menus),
            "buttons_by_model": {k: sorted(v) for k, v in buttons_by_model.items()},
            "tabs_by_model": {k: sorted(v) for k, v in tabs_by_model.items()},
            "fields_by_model": fields_by_model,
            "model_rules": model_rules,
            "model_ui": model_ui,
            "hidden_reports_by_model": {
                k: sorted(v) for k, v in hidden_reports_by_model.items()
            },
            "hidden_sidebar_action_ids_by_model": {
                k: sorted(v) for k, v in hidden_sidebar_action_ids_by_model.items()
            },
        }
        return json.dumps(payload, sort_keys=True)

    @api.model
    def rules_payload_for_user(self):
        """Same JSON as ``session_info['aac_rules_json']``; exposed for RPC so the web client
        can refresh rules without a full reload (SPA session snapshot stays stale otherwise)."""
        return self._rules_payload_json()

    @api.model
    def _rules_dict(self):
        data = json.loads(self._rules_payload_json())
        if data.get("empty"):
            return None
        return data

    @api.model
    def _audit_denial(self, model_name, operation, detail):
        rules = self._rules_dict()
        if not rules or not rules.get("audit"):
            return
        
        # Use a separate cursor to ensure logs are saved even if the main transaction is rolled back (AccessError).
        try:
            with self.pool.cursor() as new_cr:
                # Use SUPERUSER_ID to bypass any further access checks for the log entry itself.
                new_env = api.Environment(new_cr, SUPERUSER_ID, self.env.context)
                pol_ids = rules.get("policy_ids", [])
                pol_id = pol_ids[0] if pol_ids else False
                new_env["advanced.access.audit.log"].create({
                    "policy_id": pol_id,
                    "user_id": self.env.uid,
                    "model_name": model_name,
                    "operation": operation,
                    "detail": detail[:10000] if detail else "",
                })
                new_cr.commit()
        except Exception:
            _logger.exception("Advanced access audit log failed")

    @api.model
    def global_readonly_whitelist(self):
        return _GLOBAL_RO_WHITELIST
