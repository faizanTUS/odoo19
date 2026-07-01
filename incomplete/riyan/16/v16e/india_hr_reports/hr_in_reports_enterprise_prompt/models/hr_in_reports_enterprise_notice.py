# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrInReportsEnterpriseNotice(models.TransientModel):
    _name = "hr.in.reports.enterprise.notice"
    _description = "Enterprise-only HR reporting notice"

    body = fields.Text(readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        res["body"] = _(
            "Payroll, India statutory registers, and Planning shift reports require Odoo "
            "Enterprise. The Community edition of **HR India Reports** intentionally omits "
            "these sub-modules because the underlying apps (hr_payroll, l10n_in_hr_payroll, "
            "planning) are only shipped with Enterprise.\n\n"
            "On Enterprise: install **HR India Reports — Payroll** (technical name: "
            "hr_in_reports_payroll) for register, bank advice, and pivot views. For "
            "PF/ESI/PT/TDS add **HR India Reports — India Payroll Statutory** "
            "(hr_in_reports_payroll_in) with Indian payroll localization. For shift, "
            "capacity, and forecast XLSX/PDF exports add **HR India Reports — Planning** "
            "(hr_in_reports_planning).\n\n"
            "If exports list no lines, confirm payslips are **Validated** or **Paid** "
            "(not Draft).\n\n"
            "Contact your Odoo partner for Enterprise licensing."
        )
        return res
