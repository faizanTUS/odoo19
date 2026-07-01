# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.exceptions import AccessError

from .cockpit_dashboard_layout import collect_dashboard_layout
from .cockpit_registry import iter_cockpit_providers


# Map cockpit segment keys to Odoo module technical names (install check).
_SEGMENT_MODULE = {
    "attendance": "hr_attendance",
    "leave": "hr_holidays",
    "expense": "hr_expense",
    "recruitment": "hr_recruitment",
    "fleet": "fleet",
    "payroll": "hr_payroll",
    "payroll_in": "l10n_in_hr_payroll",
    "planning": "planning",
}


class HrInCockpit(models.TransientModel):
    """Transient service model for cockpit JSON (ORM-friendly ACL; no business rows)."""

    _name = "hr.in.cockpit"
    _description = "HR Reports Cockpit aggregate API"

    @api.model
    def _module_installed(self, module_name):
        mod = self.env["ir.module.module"].sudo().search(
            [("name", "=", module_name)], limit=1
        )
        return bool(mod and mod.state == "installed")

    @api.model
    def _validate_filters_companies(self, filters):
        """Ensure requested company_ids ⊆ allowed_company_ids."""
        if not filters:
            return
        company_ids = filters.get("company_ids")
        if not company_ids:
            return
        allowed = set(self.env.context.get("allowed_company_ids", []) or [])
        if not allowed:
            allowed = {self.env.company.id}
        bad = set(company_ids) - allowed
        if bad:
            raise AccessError(self.env._("Invalid company scope for cockpit."))

    @api.model
    def get_dashboard_payload(self, filters=None):
        """Return JSON-serializable cockpit payload (see plan §6.2)."""
        access = self.env["hr.in.report.access"]
        access.assert_reports_access()
        self._validate_filters_companies(filters or {})
        access.validate_cockpit_filter_employees(filters or {})
        segments = []
        for key, provider_cls in iter_cockpit_providers():
            mod_name = _SEGMENT_MODULE.get(key)
            if mod_name and not self._module_installed(mod_name):
                continue
            collect = getattr(provider_cls, "collect", None)
            if not callable(collect):
                continue
            segment = collect(self.env, filters or {})
            if segment:
                segments.append(segment)
        currency = self.env.company.currency_id.name
        layout = collect_dashboard_layout(self.env, filters or {})
        return {
            "meta": {
                "schema_version": 8,
                "currency": currency,
                "companies": list(self.env.context.get("allowed_company_ids", []) or [self.env.company.id]),
            },
            "filters_echo": filters or {},
            "layout": layout,
            "segments": segments,
        }
