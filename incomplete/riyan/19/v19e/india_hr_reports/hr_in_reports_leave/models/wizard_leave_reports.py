# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields, models

from .leave_report_formatting import enrich_leave_pdf_context
from .leave_xlsx_export import export_leave_xlsx_professional


def _selection_label(env, comodel_name, field_name, value):
    field = env[comodel_name]._fields[field_name]
    return dict(field._description_selection(env)).get(value, value)


class HrInReportWizardLeaveLedger(models.TransientModel):
    _name = "hr.in.report.wizard.leave.ledger"
    _description = "Leave ledger by employee"
    _inherit = ["hr.in.report.wizard.mixin"]

    def _get_pdf_render_context(self):
        return enrich_leave_pdf_context(self, super()._get_pdf_render_context())

    def action_export_xlsx(self):
        return export_leave_xlsx_professional(self)

    def _pdf_report_xmlid(self):
        return "india_hr_reports.action_report_leave_ledger"

    def _leave_domain(self):
        dom = [
            ("employee_id.company_id", "in", self.company_ids.ids),
            ("request_date_from", "<=", self.date_to),
            ("request_date_to", ">=", self.date_from),
        ]
        if self.department_ids:
            dom.append(("employee_id.department_id", "in", self.department_ids.ids))
        dom += self._report_employee_domain()
        return dom

    def _get_dataset(self):
        self.ensure_one()
        leaves = self.env["hr.leave"].search(self._leave_domain(), order="employee_id,request_date_from")
        self._enforce_row_cap(len(leaves))
        cols = [
            ("employee", self.env._("Employee")),
            ("department", self.env._("Department")),
            ("leave_type", self.env._("Leave type")),
            ("date_from", self.env._("From")),
            ("date_to", self.env._("To")),
            ("days", self.env._("Days")),
            ("state", self.env._("State")),
        ]
        rows = []
        for lv in leaves:
            rows.append(
                {
                    "employee": lv.employee_id.display_name,
                    "department": lv.employee_id.department_id.name or "",
                    "leave_type": lv.holiday_status_id.name or "",
                    "date_from": lv.request_date_from,
                    "date_to": lv.request_date_to,
                    "days": lv.number_of_days,
                    "state": _selection_label(self.env, "hr.leave", "state", lv.state),
                }
            )
        return {
            "title": self.env._("Leave ledger"),
            "filename": "in_leave_ledger",
            "sheet_name": "leave",
            "columns": cols,
            "rows": rows,
        }


class HrInReportWizardLeaveBalance(models.TransientModel):
    _name = "hr.in.report.wizard.leave.balance"
    _description = "Leave balance as-of date"
    _inherit = ["hr.in.report.wizard.mixin"]

    def _get_pdf_render_context(self):
        return enrich_leave_pdf_context(self, super()._get_pdf_render_context())

    def action_export_xlsx(self):
        return export_leave_xlsx_professional(self)

    def _pdf_report_xmlid(self):
        return "india_hr_reports.action_report_leave_balance"

    def _get_dataset(self):
        self.ensure_one()
        as_of = self.date_to
        Alloc = self.env["hr.leave.allocation"]
        alloc_dom = [
            ("employee_id.company_id", "in", self.company_ids.ids),
            ("date_from", "<=", as_of),
            "|",
            ("date_to", "=", False),
            ("date_to", ">=", as_of),
        ]
        if self.department_ids:
            alloc_dom.append(("employee_id.department_id", "in", self.department_ids.ids))
        alloc_dom += self._report_employee_domain()
        allocs = Alloc.search(alloc_dom)
        self._enforce_row_cap(len(allocs))
        cols = [
            ("employee", self.env._("Employee")),
            ("leave_type", self.env._("Leave type")),
            ("allocated", self.env._("Allocated")),
            ("valid_from", self.env._("Valid from")),
            ("valid_to", self.env._("Valid to")),
        ]
        rows = []
        for a in allocs:
            rows.append(
                {
                    "employee": a.employee_id.display_name,
                    "leave_type": a.holiday_status_id.name or "",
                    "allocated": a.number_of_days,
                    "valid_from": a.date_from,
                    "valid_to": a.date_to or "",
                }
            )
        return {
            "title": self.env._("Leave balance (allocations as-of)"),
            "filename": "in_leave_balance",
            "sheet_name": "balance",
            "columns": cols,
            "rows": rows,
        }


class HrInReportWizardLeaveAccrual(models.TransientModel):
    _name = "hr.in.report.wizard.leave.accrual"
    _description = "Accrual allocation audit"
    _inherit = ["hr.in.report.wizard.mixin"]

    def _get_pdf_render_context(self):
        return enrich_leave_pdf_context(self, super()._get_pdf_render_context())

    def action_export_xlsx(self):
        return export_leave_xlsx_professional(self)

    def _pdf_report_xmlid(self):
        return "india_hr_reports.action_report_leave_accrual"

    def _get_dataset(self):
        self.ensure_one()
        end = self.date_to + timedelta(days=1)
        dom = [
            ("employee_id.company_id", "in", self.company_ids.ids),
            ("create_date", ">=", fields.Datetime.to_datetime(self.date_from)),
            ("create_date", "<", fields.Datetime.to_datetime(end)),
        ]
        if self.department_ids:
            dom.append(("employee_id.department_id", "in", self.department_ids.ids))
        dom += self._report_employee_domain()
        allocs = self.env["hr.leave.allocation"].search(dom, order="create_date")
        self._enforce_row_cap(len(allocs))
        cols = [
            ("employee", self.env._("Employee")),
            ("leave_type", self.env._("Leave type")),
            ("days", self.env._("Days")),
            ("date_from", self.env._("From")),
            ("date_to", self.env._("To")),
            ("state", self.env._("State")),
            ("created", self.env._("Created on")),
        ]
        rows = []
        for a in allocs:
            rows.append(
                {
                    "employee": a.employee_id.display_name,
                    "leave_type": a.holiday_status_id.name or "",
                    "days": a.number_of_days,
                    "date_from": a.date_from,
                    "date_to": a.date_to or "",
                    "state": _selection_label(
                        self.env, "hr.leave.allocation", "state", a.state
                    ),
                    "created": a.create_date,
                }
            )
        return {
            "title": self.env._("Accrual allocation audit"),
            "filename": "in_leave_accrual_audit",
            "sheet_name": "accrual",
            "columns": cols,
            "rows": rows,
        }
