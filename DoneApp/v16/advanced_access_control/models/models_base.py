# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
import ast
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


def _aac_apply_modifier_to_node(node, mod, expr):
    """Apply a modifier (invisible/readonly/required) to a field node.
    Handles Odoo 16's attrs and modifiers for both legacy and OWL views.
    """
    expr = (expr or "").strip()
    if not expr or expr == "1":
        # Static modifier
        if mod == "readonly":
            prev = node.get("readonly")
            if prev and prev not in ("0", "False"):
                return
            node.set("readonly", "1")
        else:
            node.set(mod, "1")
        # Also update modifiers for OWL consistency
        import json
        modifiers_raw = node.get("modifiers") or "{}"
        try:
            mods = json.loads(modifiers_raw)
        except:
            mods = {}
        mods[mod] = True
        node.set("modifiers", json.dumps(mods))
        return

    # Dynamic modifier (Odoo 16 style: use attrs + modifiers)
    domain_str = expr
    if not expr.startswith("["):
        # Conversion for simple Python-like expressions to Odoo domains
        if "==" in expr:
            parts = [p.strip() for p in expr.split("==", 1)]
            if len(parts) == 2:
                f, v = parts[0], parts[1].strip("'").strip('"')
                domain_str = "[('%s', '=', '%s')]" % (f, v)
        elif "!=" in expr:
            parts = [p.strip() for p in expr.split("!=", 1)]
            if len(parts) == 2:
                f, v = parts[0], parts[1].strip("'").strip('"')
                domain_str = "[('%s', '!=', '%s')]" % (f, v)

    # 1. Update attrs (Legacy views)
    attrs_raw = node.get("attrs") or "{}"
    try:
        attrs = ast.literal_eval(attrs_raw)
    except:
        attrs = {}

    try:
        new_domain = ast.literal_eval(domain_str)
        if not isinstance(new_domain, list):
            new_domain = [("1", "=", "1")]
    except:
        # Fallback to constant true if literal eval fails
        new_domain = [("1", "=", "1")]

    prev_domain = attrs.get(mod)
    if prev_domain:
        if isinstance(prev_domain, list):
            attrs[mod] = ["|"] + prev_domain + new_domain
        else:
            attrs[mod] = new_domain
    else:
        attrs[mod] = new_domain

    node.set("attrs", str(attrs))

    # 2. Update modifiers (OWL views)
    import json
    modifiers_raw = node.get("modifiers") or "{}"
    try:
        mods = json.loads(modifiers_raw)
    except:
        mods = {}
    
    # Odoo 16 modifiers often use domains for dynamic values
    mods[mod] = attrs[mod]
    node.set("modifiers", json.dumps(mods))

    # In Odoo 16, static readonly="1" overrides dynamic attrs/modifiers
    if mod == "readonly" and node.get("readonly") in ("1", "True"):
        node.attrib.pop("readonly")


class Base(models.AbstractModel):
    _inherit = "base"

    def _aac_apply_arch_restrictions(self, arch, view_type):
        """Apply AAC view-arch mutations (hide buttons/pages, readonly flags, import/export attrs).

        Note: Odoo 16 OWL view loading uses `get_view/get_views`, not `fields_view_get`,
        so we need to mutate the arch there as well.
        """
        if not arch:
            return arch
        svc = self.env["advanced.access.service"]
        rules = svc._rules_dict()
        if not rules:
            return arch

        root = etree.fromstring(arch.encode("utf-8"))

        # In Odoo 16 the view_type for list views is often 'tree'
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

        # Hide form buttons and notebook pages only on form views.
        if view_type == "form" and root.tag == "form":
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
                    # Keep fields alive for modifiers/defaultExportList/etc even if the tab is removed.
                    if preserve_names:
                        anchor = root.find(".//sheet")
                        if anchor is None:
                            anchor = root
                        still_there = _aac_root_field_names_under(anchor)
                        to_preserve = sorted(preserve_names - still_there)
                        if to_preserve:
                            # Use an invisible group container to ensure these fields don't leak into the UI.
                            # We keep them in the arch so that modifiers/domains on other fields don't break.
                            pool = etree.SubElement(anchor, "group", {
                                "invisible": "1",
                                "modifiers": '{"invisible": true}',
                                "class": "o_aac_preserved_fields"
                            })
                            for fname in to_preserve:
                                etree.SubElement(pool, "field", {
                                    "name": fname,
                                    "invisible": "1",
                                    "modifiers": '{"invisible": true}'
                                })

        # Field modifiers: apply on any view type (form + list/tree subviews might need it).
        for spec in rules.get("fields_by_model", {}).get(self._name, []):
            fname = spec["field"]
            mod = spec["modifier"]
            expr = spec.get("expr")
            for node in root.iter("field"):
                if node.get("name") == fname:
                    _aac_apply_modifier_to_node(node, mod, expr)

        return etree.tostring(root, encoding="unicode").replace("\t", "")

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
        if user.has_group("advanced_access_control.group_advanced_access_manager"):
            return False
        return True

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """Odoo 16 OWL view pipeline: mutate returned arch for this user."""
        res = super().get_view(view_id=view_id, view_type=view_type, **options)
        if self.env.su or not self._aac_should_enforce():
            return res
        # Bypass for users without policies / managers is handled in service payload.
        try:
            arch = res.get("arch")
            res["arch"] = self._aac_apply_arch_restrictions(arch, view_type)
        except Exception:
            # Never block view loading due to AAC patching; fail open but log would be noisy.
            return res
        return res

    def _aac_enforce_operation(self, operation):
        """Raise AccessError if AAC rules forbid ``operation`` (create/write/unlink) on self.

        This replaces the Odoo 16 ``_check_access`` hook which does not exist in Odoo 16.
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
        # This replaces the Odoo-16 _check_access hook which does not exist in Odoo 16.
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
    def fields_view_get(self, view_id=None, view_type="form", toolbar=False, submenu=False):
        result = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
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

        # In Odoo 16 the view_type for list views is often 'tree'
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
                if preserve_names and view_type == "form" and root.tag == "form":
                    anchor = root.find(".//sheet")
                    if anchor is None:
                        anchor = root
                    still_there = _aac_root_field_names_under(anchor)
                    to_preserve = sorted(preserve_names - still_there)
                    if to_preserve:
                        # Use an invisible group container to ensure these fields don't leak into the UI.
                        pool = etree.SubElement(anchor, "group", {
                            "invisible": "1",
                            "modifiers": '{"invisible": true}',
                            "class": "o_aac_preserved_fields"
                        })
                        for fname in to_preserve:
                            etree.SubElement(pool, "field", {
                                "name": fname,
                                "invisible": "1",
                                "modifiers": '{"invisible": true}'
                            })

        for spec in rules.get("fields_by_model", {}).get(self._name, []):
            fname = spec["field"]
            mod = spec["modifier"]
            expr = spec.get("expr")
            for node in root.iter("field"):
                if node.get("name") == fname:
                    _aac_apply_modifier_to_node(node, mod, expr)

        result["arch"] = etree.tostring(root, encoding="unicode").replace("\t", "")

        # Sidebar (toolbar) filtering for Odoo 16
        if toolbar and result.get("toolbar"):
            # 1. Reports (Print menu)
            h_reports = set(rules.get("hidden_reports_by_model", {}).get(self._name, []))
            if h_reports and result["toolbar"].get("print"):
                result["toolbar"]["print"] = [
                    r
                    for r in result["toolbar"]["print"]
                    if r.get("id") not in h_reports
                ]

            # 2. Actions (Action menu)
            h_actions = set(
                rules.get("hidden_sidebar_action_ids_by_model", {}).get(self._name, [])
            )
            if h_actions:
                if result["toolbar"].get("action"):
                    result["toolbar"]["action"] = [
                        a
                        for a in result["toolbar"]["action"]
                        if a.get("id") not in h_actions
                    ]
                if result["toolbar"].get("relate"):
                    result["toolbar"]["relate"] = [
                        a
                        for a in result["toolbar"]["relate"]
                        if a.get("id") not in h_actions
                    ]

        return result
