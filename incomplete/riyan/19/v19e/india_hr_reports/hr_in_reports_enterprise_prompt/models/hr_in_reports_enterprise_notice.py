# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrInReportsEnterpriseNotice(models.TransientModel):
    _name = "hr.in.reports.enterprise.notice"
    _description = "Enterprise-only HR reporting notice"

    body = fields.Text(readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        res["body"] = self.env._(
            "Payroll and India statutory registers need Odoo Enterprise with the Payroll app "
            "(hr_payroll).\n\n"
            "On Enterprise: install **HR India Reports — Payroll** (technical name: "
            "hr_in_reports_payroll), then open Reporting → HR Reports → **Payroll** for the "
            "register, bank advice, and pivot. For PF/ESI/PT/TDS, add **HR India Reports — "
            "India Payroll Statutory** (hr_in_reports_payroll_in) with Indian payroll "
            "localization.\n\n"
            "If exports list no lines, confirm payslips are **Validated** or **Paid** "
            "(not Draft).\n\n"
            "Contact your Odoo partner for Enterprise licensing."
        )
        return res
