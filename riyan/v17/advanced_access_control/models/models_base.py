# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from lxml import etree

from odoo import api, models, _
from odoo.exceptions import AccessError


def _aac_is_root_field_under(field_el, container_el):
    """True if ``field_el`` is under ``container_el`` without crossing another named ``<field/>`` (x2many subview)."""
    p = field_el.getparent()
    while p is not None:
        if p is container_el:
            return True
        if p.tag == "field" and p.get("name"):
            return False
        p = p.getparent()
    return False


def _aac_root_field_names_under(container_el):
    """Technical names of fields that belong to the form's main model (not inside order_line / nested subviews)."""
    names = set()
    for fel in container_el.iter("field"):
        fname = fel.get("name")
        if fname and _aac_is_root_field_under(fel, container_el):
            names.add(fname)
    return names


def _aac_root_field_names_in_pages(pages):
    """Collect main-model field names declared only inside the given notebook pages."""
    names = set()
    for page in pages:
        for fel in page.iter("field"):
            fname = fel.get("name")
            if fname and _aac_is_root_field_under(fel, page):
                names.add(fname)
    return names


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def _aac_should_enforce(self):
        """When False, Advanced Access Control is not applied (server + view hooks)."""
        env = self.env
        if env.su:
            return False
        user = env.user
        if not user:
            return True
        if user._is_superuser():
            return False
        su = user.sudo()
        if su._is_system() or su.has_group("base.group_erp_manager"):
            return False
        if su.has_group("advanced_access_control.group_advanced_access_manager"):
            return False
        return True

    def _aac_enforce_operation(self, operation):
        """Raise AccessError if AAC rules forbid ``operation`` (create/write/unlink) on self.

        This replaces the Odoo 18 ``_check_access`` hook which does not exist in Odoo 17.
        Call this at the top of write(), create(), and unlink() overrides.
        """
        if self.env.su or not self._aac_should_enforce():
            return
        svc = self.env["advanced.access.service"]
        rules = svc._rules_dict()
        if not rules:
            return

        model = self._name

        # --- global readonly ---
        if rules.get("global_readonly") and model not in svc.global_readonly_whitelist():
            svc._audit_denial(model, operation, "global_readonly")
            raise AccessError(
                _("This database is read-only for you (Advanced Access Control).")
            )

        # --- per-model rules ---
        model_rules = [r for r in rules.get("model_rules", []) if r["model"] == model]

        if operation == "create" and model_rules:
            if any(not r["allow_create"] for r in model_rules):
                svc._audit_denial(model, operation, "model rule deny create")
                raise AccessError(
                    _("You are not allowed to create %(model)s records (Advanced Access Control).")
                    % {"model": model}
                )

        denied = self._aac_rule_denied_subset(operation, model_rules)
        if denied:
            svc._audit_denial(
                model,
                operation,
                "policy model rule (%s records)" % len(denied),
            )
            raise AccessError(
                _("You are not allowed to %(op)s on %(model)s (Advanced Access Control).")
                % {"op": operation, "model": model}
            )

    def _aac_rule_denied_subset(self, operation, model_rules):
        key = {
            "read": "allow_read",
            "write": "allow_write",
            "unlink": "allow_unlink",
        }.get(operation)
        if not key or not model_rules:
            return self.browse()

        denied = self.browse()
        for rule in model_rules:
            if rule[key]:
                continue
            dom = rule["domain"]
            if not dom:
                return self
            try:
                denied |= self & self.filtered_domain(dom)
            except Exception:
                denied |= self
        return denied

    def _aac_archive_write_forbidden_subset(self, rules):
        """Subset of self that may not change ``active`` (archive/unarchive) under policy rules."""
        if not self:
            return self.browse()
        model = self._name
        if rules.get("global_disable_archive"):
            return self
        forbidden = self.browse()
        for rule in rules.get("model_rules", []):
            if rule["model"] != model or rule.get("allow_archive", True):
                continue
            dom = rule["domain"]
            if not dom:
                return self
            try:
                forbidden |= self & self.filtered_domain(dom)
            except Exception:
                forbidden |= self
        return forbidden

    def write(self, vals):
        # Enforce AAC rules on every write (global-readonly + model rules).
        # This replaces the Odoo-18 _check_access hook which does not exist in Odoo 17.
        self._aac_enforce_operation("write")

        # Archive / unarchive restriction (active field)
        if "active" in vals and not self.env.su and self._aac_should_enforce():
            svc = self.env["advanced.access.service"]
            rules = svc._rules_dict()
            if rules:
                bad = self._aac_archive_write_forbidden_subset(rules)
                if self & bad:
                    svc._audit_denial(self._name, "write", "archive/unarchive denied")
                    raise AccessError(
                        _(
                            "Archiving or unarchiving is not allowed for this record "
                            "(Advanced Access Control)."
                        )
                    )
        return super().write(vals)

    def unlink(self):
        # Enforce AAC rules on delete (global-readonly + model unlink rules).
        self._aac_enforce_operation("unlink")
        return super().unlink()

    @api.model_create_multi
    def create(self, vals_list):
        # Enforce AAC rules on create (global-readonly + model create rules).
        # _aac_enforce_operation works on self (empty recordset for @model_create_multi).
        self._aac_enforce_operation("create")
        return super().create(vals_list)

    def copy(self, default=None):
        self.ensure_one()
        svc = self.env["advanced.access.service"]
        rules = svc._rules_dict()
        if rules and not self.env.su and self._aac_should_enforce():
            for rule in rules.get("model_rules", []):
                if rule["model"] != self._name or rule["allow_duplicate"]:
                    continue
                dom = rule["domain"]
                if not dom:
                    svc._audit_denial(self._name, "duplicate", "model rule")
                    raise AccessError(
                        _("Duplicating this record is not allowed (Advanced Access Control).")
                    )
                try:
                    if self.filtered_domain(dom):
                        svc._audit_denial(self._name, "duplicate", "model rule (domain)")
                        raise AccessError(
                            _("Duplicating this record is not allowed (Advanced Access Control).")
                        )
                except AccessError:
                    raise
                except Exception:
                    svc._audit_denial(self._name, "duplicate", "model rule (domain eval)")
                    raise AccessError(
                        _("Duplicating this record is not allowed (Advanced Access Control).")
                    )
        return super().copy(default=default)

    def export_data(self, fields_to_export):
        svc = self.env["advanced.access.service"]
        rules = svc._rules_dict()
        if rules and not self.env.su and self._aac_should_enforce():
            if rules.get("global_disable_export"):
                svc._audit_denial(self._name, "export", "global_disable_export")
                raise AccessError(
                    _("Export is not allowed for your user (Advanced Access Control).")
                )
            for rule in rules.get("model_rules", []):
                if rule["model"] != self._name or rule["allow_export"]:
                    continue
                dom = rule["domain"]
                if not dom:
                    svc._audit_denial(self._name, "export", "model rule")
                    raise AccessError(
                        _("Export is not allowed for this model (Advanced Access Control).")
                    )
                try:
                    overlap = self & self.filtered_domain(dom)
                except Exception:
                    overlap = self
                if overlap:
                    svc._audit_denial(self._name, "export", "model rule (domain)")
                    raise AccessError(
                        _("Export is not allowed for the selected records (Advanced Access Control).")
                    )
        return super().export_data(fields_to_export)

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields, attributes)
        if self.env.su or not self._aac_should_enforce():
            return res
        svc = self.env["advanced.access.service"]
        rules = svc._rules_dict()
        if not rules:
            return res
        if rules.get("global_disable_export"):
            for finfo in res.values():
                finfo["exportable"] = False
            return res
        for rule in rules.get("model_rules", []):
            if rule["model"] != self._name:
                continue
            if rule["allow_export"] or rule["domain"]:
                continue
            for finfo in res.values():
                finfo["exportable"] = False
        return res

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        # NOTE (Odoo 17): get_views() converts view_type 'list' → 'tree' before
        # calling this method. So we must match either 'list' or 'tree' for list views.
        result = super().get_view(view_id, view_type, **options)
        if self.env.su or not self._aac_should_enforce():
            return result
        svc = self.env["advanced.access.service"]
        rules = svc._rules_dict()
        if not rules:
            return result

        arch = result.get("arch")
        if not arch:
            return result

        root = etree.fromstring(arch.encode("utf-8"))

        # In Odoo 17 the view_type for list views is always 'tree' (not 'list')
        is_list_view = view_type in ("list", "tree") and root.tag in ("list", "tree")

        caps = (rules.get("model_ui") or {}).get(self._name)
        if caps:
            if view_type == "form" and root.tag == "form":
                if not caps.get("write", True):
                    root.set("edit", "false")
                if not caps.get("create", True):
                    root.set("create", "false")
                if not caps.get("unlink", True):
                    root.set("delete", "false")
                if not caps.get("duplicate", True):
                    root.set("duplicate", "false")
            elif is_list_view:
                if not caps.get("write", True):
                    root.set("edit", "false")
                if not caps.get("create", True):
                    root.set("create", "false")
                if not caps.get("unlink", True):
                    root.set("delete", "false")
                if not caps.get("duplicate", True):
                    root.set("duplicate", "false")
                if rules.get("global_disable_import") or not caps.get("import", True):
                    root.set("import", "false")
                if rules.get("global_disable_export") or not caps.get("export", True):
                    root.set("export_xlsx", "false")

        if is_list_view and not caps:
            if rules.get("global_disable_import"):
                root.set("import", "false")
            if rules.get("global_disable_export"):
                root.set("export_xlsx", "false")

        if rules.get("global_readonly"):
            if view_type == "form" and root.tag == "form":
                root.set("edit", "false")
                root.set("create", "false")
                root.set("delete", "false")
                root.set("duplicate", "false")
            elif is_list_view:
                root.set("create", "false")
                root.set("delete", "false")
                root.set("edit", "false")

        bmap = set(rules.get("buttons_by_model", {}).get(self._name, []))
        if bmap:
            for btn in list(root.iter("button")):
                name = btn.get("name")
                if name and name in bmap and btn.getparent() is not None:
                    btn.getparent().remove(btn)

        tmap = set(rules.get("tabs_by_model", {}).get(self._name, []))
        if tmap:
            pages_to_remove = [
                p
                for p in list(root.iter("page"))
                if p.get("string")
                and p.get("string") in tmap
                and p.getparent() is not None
            ]
            if pages_to_remove:
                preserve_names = _aac_root_field_names_in_pages(pages_to_remove)
                for page in pages_to_remove:
                    page.getparent().remove(page)
                # Dropping a tab removes its <field/> nodes from the arch; header buttons and modifiers
                # may still reference those names (e.g. sale.order ``invoice_status`` on "Other Info").
                if preserve_names and view_type == "form" and root.tag == "form":
                    anchor = root.find(".//sheet")
                    if anchor is None:
                        anchor = root
                    still_there = _aac_root_field_names_under(anchor)
                    for fname in sorted(preserve_names - still_there):
                        etree.SubElement(anchor, "field", {"name": fname, "invisible": "1"})

        for spec in rules.get("fields_by_model", {}).get(self._name, []):
            fname = spec["field"]
            mod = spec["modifier"]
            expr = (spec.get("expr") or "").strip()
            for node in root.iter("field"):
                if node.get("name") != fname:
                    continue
                val = expr if expr else "1"
                if mod == "invisible":
                    node.set("invisible", val)
                elif mod == "readonly":
                    prev = node.get("readonly")
                    if prev:
                        node.set("readonly", "(%s) or (%s)" % (prev, val))
                    else:
                        node.set("readonly", val)
                elif mod == "required":
                    prev = node.get("required")
                    if prev:
                        node.set("required", "(%s) or (%s)" % (prev, val))
                    else:
                        node.set("required", val)

        result["arch"] = etree.tostring(root, encoding="unicode").replace("\t", "")
        return result
