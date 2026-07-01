# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from collections import defaultdict

from odoo import models


class HrInReportWizardExpConsolidated(models.TransientModel):
    _name = "hr.in.report.wizard.exp.consolidated"
    _description = "Employee-wise consolidated claims"
    _inherit = ["hr.in.report.wizard.mixin"]

    def _pdf_report_xmlid(self):
        return "india_hr_reports_community.action_report_exp_consolidated"

    def _professional_pdf_sum_column_keys(self):
        return ["total_amount"]

    def _exp_domain(self):
        dom = [
            ("company_id", "in", self.company_ids.ids),
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
        ]
        if self.department_ids:
            dom.append(("employee_id.department_id", "in", self.department_ids.ids))
        dom += self._report_employee_domain()
        return dom

    def _line_amount(self, line):
        if "total_amount_currency" in line._fields and line.total_amount_currency:
            return line.total_amount_currency
        return (line.unit_amount or 0.0) * (line.quantity or 1.0)

    def _get_dataset(self):
        self.ensure_one()
        lines = self.env["hr.expense"].search(self._exp_domain())
        self._enforce_row_cap(len(lines))
        totals = defaultdict(float)
        for x in lines:
            totals[x.employee_id.id] += self._line_amount(x)
        cols = [
            ("employee", "Employee"),
            ("department", "Department"),
            ("total_amount", "Total amount"),
        ]
        rows = []
        for eid, amt in sorted(totals.items(), key=lambda x: -x[1]):
            emp = self.env["hr.employee"].browse(eid)
            rows.append(
                {
                    "employee": emp.display_name,
                    "department": emp.department_id.name or "",
                    "total_amount": round(amt, 2),
                }
            )
        return {
            "title": "Employee-wise consolidated claims",
            "filename": "in_exp_consolidated_claims",
            "sheet_name": "claims",
            "columns": cols,
            "rows": rows,
        }


class HrInReportWizardExpProductAnalytic(models.TransientModel):
    _name = "hr.in.report.wizard.exp.product_analytic"
    _description = "Claims by product & analytic"
    _inherit = ["hr.in.report.wizard.mixin"]

    def _pdf_report_xmlid(self):
        return "india_hr_reports_community.action_report_exp_product_analytic"

    def _professional_pdf_sum_column_keys(self):
        return ["amount"]

    def _line_amount(self, line):
        if "total_amount_currency" in line._fields and line.total_amount_currency:
            return line.total_amount_currency
        return (line.unit_amount or 0.0) * (line.quantity or 1.0)

    def _get_dataset(self):
        self.ensure_one()
        dom = [
            ("company_id", "in", self.company_ids.ids),
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
        ]
        if self.department_ids:
            dom.append(("employee_id.department_id", "in", self.department_ids.ids))
        dom += self._report_employee_domain()
        lines = self.env["hr.expense"].search(dom)
        self._enforce_row_cap(len(lines))
        cols = [
            ("employee", "Employee"),
            ("product", "Product"),
            ("analytic", "Analytic summary"),
            ("amount", "Total"),
            ("state", "State"),
        ]
        rows = []
        for x in lines:
            analytic = ""
            if getattr(x, "analytic_distribution", None):
                analytic = str(x.analytic_distribution)
            rows.append(
                {
                    "employee": x.employee_id.display_name,
                    "product": x.product_id.display_name if x.product_id else "",
                    "analytic": analytic,
                    "amount": round(self._line_amount(x), 2),
                    "state": x.state,
                }
            )
        return {
            "title": "Claims by product & analytic",
            "filename": "in_exp_by_product_analytic",
            "sheet_name": "expense",
            "columns": cols,
            "rows": rows,
        }
