# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


def _aac_domain_leaf_tuples(domain):
    """Yield (field, op, value) leaves from a nested domain."""
    if not domain:
        return
    for item in domain:
        if isinstance(item, (list, tuple)) and len(item) == 3 and isinstance(item[0], str):
            if item[0] not in ("&", "|", "!"):
                yield item
        elif isinstance(item, (list, tuple)):
            yield from _aac_domain_leaf_tuples(item)


def _aac_model_ids_from_domain(domain):
    ids = set()
    for name, op, val in _aac_domain_leaf_tuples(domain):
        if name != "model_id":
            continue
        if op == "=" and val:
            ids.add(val)
        elif op == "in" and val:
            ids.update(val)
    return ids


class AdvancedAccessFormButton(models.Model):
    """Indexed ``<button name="..."/>`` from combined form views, for policy pickers."""

    _name = "advanced.access.form.button"
    _description = "Form button name index"
    _order = "model_id, button_label, xml_name"
    _rec_name = "xml_name"
    _rec_names_search = ["xml_name", "button_label"]

    model_id = fields.Many2one("ir.model", required=True, ondelete="cascade", index=True)
    xml_name = fields.Char(
        string="Button name",
        required=True,
        help="XML name attribute of the button.",
    )
    button_label = fields.Char(
        string="Label",
        help="Button string from the view when present.",
    )

    _sql_constraints = [
        (
            "aac_form_button_model_xml_unique",
            "unique(model_id, xml_name)",
            "This button name is already indexed for this model.",
        ),
    ]

    def name_get(self):
        res = []
        for rec in self:
            lab = rec.button_label
            xm = rec.xml_name
            if lab and lab != xm:
                res.append((rec.id, "%s (%s)" % (lab, xm)))
            else:
                res.append((rec.id, xm))
        return res

    @api.model
    def _aac_resolved_view_model_name(self, view):
        """Inherited form views may leave ``model`` empty; walk to the root view."""
        v = view.sudo()
        seen = set()
        while v and v.id not in seen:
            seen.add(v.id)
            if v.model:
                return v.model
            v = v.inherit_id
        return None

    @api.model
    def _aac_catalog_rebuild_needed(self, domain):
        """True if we should rebuild before retrying a search (empty catalog or no rows for model)."""
        if self.env.context.get("aac_form_button_skip_rebuild_retry"):
            return False
        mids = _aac_model_ids_from_domain(domain)
        sudo_self = self.sudo()
        if not sudo_self.search_count([]):
            return True
        if not mids:
            return False
        for mid in mids:
            if not sudo_self.search_count([("model_id", "=", mid)], limit=1):
                return True
        return False

    @api.model
    @api.readonly
    def search_fetch(self, domain, field_names, offset=0, limit=None, order=None):
        """Rebuild catalog when empty; Odoo 18 ``name_search`` uses ``search_fetch``, not ``search``."""
        res = super().search_fetch(
            domain, field_names, offset=offset, limit=limit, order=order
        )
        if res or not self._aac_catalog_rebuild_needed(domain):
            return res
        self.sudo().rebuild_index()
        return super(
            AdvancedAccessFormButton,
            self.with_context(aac_form_button_skip_rebuild_retry=True),
        ).search_fetch(
            domain, field_names, offset=offset, limit=limit, order=order
        )

    @api.model
    def rebuild_index(self):
        """Scan all form views and rebuild rows (sudo). Safe to call on upgrade."""
        sudo_self = self.sudo()
        # Use search_count (uses _search) so we do not recurse through search_fetch when the table is empty.
        if sudo_self.search_count([]):
            sudo_self.search([]).unlink()
        View = self.env["ir.ui.view"].sudo()
        IrModel = self.env["ir.model"].sudo()
        # Include inherited views with empty ``model`` (root still has the model).
        views = View.search([("type", "=", "form")])
        # (model_id, xml_name) -> best label (prefer non-empty)
        found = {}
        for view in views:
            model_name = self._aac_resolved_view_model_name(view)
            if not model_name or model_name not in self.env:
                continue
            im = IrModel.search([("model", "=", model_name)], limit=1)
            if not im:
                continue
            try:
                arch = view._get_combined_arch()
            except Exception as err:
                _logger.debug(
                    "AAC skip view %s (%s): %s", view.id, view.name, err
                )
                continue
            if arch is None:
                continue
            for el in arch.iter("button"):
                btn_name = el.get("name")
                if not btn_name or not isinstance(btn_name, str):
                    continue
                btn_name = btn_name.strip()
                if not btn_name or btn_name.startswith("%(") or "{{" in btn_name:
                    continue
                raw_label = el.get("string") or ""
                if isinstance(raw_label, str) and (
                    raw_label.strip().startswith("{{") or "{{" in raw_label
                ):
                    raw_label = ""
                label = raw_label.strip() or False
                key = (im.id, btn_name)
                if key not in found:
                    found[key] = label
                elif label and not found[key]:
                    found[key] = label
        rows = [
            {
                "model_id": mid,
                "xml_name": xname,
                "button_label": lbl or False,
            }
            for (mid, xname), lbl in found.items()
        ]
        if rows:
            self.sudo().create(rows)
        return True
