# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models

from .advanced_access_form_button import _aac_model_ids_from_domain

_logger = logging.getLogger(__name__)


class AdvancedAccessFormNotebookPage(models.Model):
    """Indexed ``<page string="..."/>`` from combined form views, for policy tab pickers."""

    _name = "advanced.access.form.notebook.page"
    _description = "Form notebook page title index"
    _order = "model_id, page_string"
    _rec_name = "page_string"

    model_id = fields.Many2one("ir.model", required=True, ondelete="cascade", index=True)
    page_string = fields.Char(
        string="Page title",
        required=True,
        help="The ``string`` attribute of the notebook page in the form view.",
    )

    _sql_constraints = [
        (
            "aac_form_notebook_page_model_string_unique",
            "unique(model_id, page_string)",
            "This notebook page title is already indexed for this model.",
        ),
    ]

    @api.model
    def _aac_resolved_view_model_name(self, view):
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
        if self.env.context.get("aac_notebook_page_skip_rebuild_retry"):
            return False
        mids = _aac_model_ids_from_domain(domain)
        sudo_self = self.sudo().with_context(aac_notebook_page_skip_rebuild_retry=True)
        if not sudo_self.search_count([]):
            return True
        if not mids:
            return False
        for mid in mids:
            if not sudo_self.search_count([("model_id", "=", mid)], limit=1):
                return True
        return False

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        """Rebuild catalog on empty search; Many2one dropdowns use _search, not search_fetch."""
        if self._aac_catalog_rebuild_needed(domain):
            self.sudo().rebuild_index()
        return super()._search(
            domain, offset=offset, limit=limit, order=order, access_rights_uid=access_rights_uid
        )

    @api.model
    def search_fetch(self, domain, field_names, offset=0, limit=None, order=None):
        """Rebuild catalog on empty search; Odoo 17 search_fetch is used by list views."""
        res = super().search_fetch(
            domain, field_names, offset=offset, limit=limit, order=order
        )
        if res or not self._aac_catalog_rebuild_needed(domain):
            return res
        self.sudo().rebuild_index()
        return super(
            AdvancedAccessFormNotebookPage,
            self.with_context(aac_notebook_page_skip_rebuild_retry=True),
        ).search_fetch(
            domain, field_names, offset=offset, limit=limit, order=order
        )

    @api.model
    def rebuild_index(self):
        sudo_self = self.sudo()
        if sudo_self.search_count([]):
            sudo_self.search([]).unlink()
        View = self.env["ir.ui.view"].sudo()
        IrModel = self.env["ir.model"].sudo()
        views = View.search([("type", "=", "form")])
        found = set()
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
            for el in arch.iter("page"):
                raw = el.get("string") or ""
                if not isinstance(raw, str):
                    continue
                if raw.strip().startswith("{{") or "{{" in raw:
                    continue
                title = raw.strip()
                if not title:
                    continue
                found.add((im.id, title))
        rows = [
            {"model_id": mid, "page_string": pstr}
            for mid, pstr in sorted(found)
        ]
        if rows:
            self.sudo().create(rows)
        return True
