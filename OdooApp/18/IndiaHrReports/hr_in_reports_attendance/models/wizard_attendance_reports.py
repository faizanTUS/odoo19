# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import timedelta

from odoo import fields, models
from odoo.tools import format_date


class HrInReportWizardAttDaily(models.TransientModel):
    _name = "hr.in.report.wizard.att.daily"
    _description = "Daily attendance register"
    _inherit = ["hr.in.report.wizard.mixin"]

    def _pdf_report_xmlid(self):
        return "IndiaHrReports.action_report_att_daily"

    def _professional_pdf_sum_column_keys(self):
        return ["worked_hours"]

    def _att_domain(self):
        end = self.date_to + timedelta(days=1)
        dom = [
            ("check_in", ">=", fields.Datetime.to_datetime(self.date_from)),
            ("check_in", "<", fields.Datetime.to_datetime(end)),
            ("employee_id.company_id", "in", self.company_ids.ids),
        ]
        if self.department_ids:
            dom.append(("employee_id.department_id", "in", self.department_ids.ids))
        dom += self._report_employee_domain()
        return dom

    def _get_dataset(self):
        self.ensure_one()
        Att = self.env["hr.attendance"].search(self._att_domain(), order="check_in")
        self._enforce_row_cap(len(Att))
        cols = [
            ("employee", "Employee"),
            ("department", "Department"),
            ("check_in", "Check in"),
            ("check_out", "Check out"),
            ("worked_hours", "Worked hours"),
        ]
        rows = []
        for a in Att:
            rows.append(
                {
                    "employee": a.employee_id.display_name,
                    "department": a.employee_id.department_id.name or "",
                    "check_in": a.check_in,
                    "check_out": a.check_out or "",
                    "worked_hours": a.worked_hours,
                }
            )
        return {
            "title": "Daily attendance register",
            "filename": "in_att_daily_register",
            "sheet_name": "attendance",
            "columns": cols,
            "rows": rows,
        }


class HrInReportWizardAttMonthly(models.TransientModel):
    _name = "hr.in.report.wizard.att.monthly"
    _description = "Monthly attendance matrix"
    _inherit = ["hr.in.report.wizard.mixin"]

    def _pdf_report_xmlid(self):
        return "IndiaHrReports.action_report_att_monthly"

    def _professional_pdf_sum_column_keys(self):
        return []

    def _get_dataset(self):
        self.ensure_one()
        if (self.date_to - self.date_from).days > 62:
            from odoo.exceptions import UserError

            raise UserError(self.env._("Pick a period of 62 days or less for the matrix export."))
        days = []
        d = self.date_from
        while d <= self.date_to:
            days.append(d)
            d += timedelta(days=1)
        Att = self.env["hr.attendance"].search(self._att_domain())
        self._enforce_row_cap(len(Att))
        by_emp_day = defaultdict(lambda: defaultdict(float))
        for a in Att:
            day = fields.Datetime.context_timestamp(self, a.check_in).date() if a.check_in else None
            if day:
                by_emp_day[a.employee_id.id][day] += a.worked_hours or 0.0
        scoped_ids = self._report_employee_ids()
        emp_ids = sorted(by_emp_day.keys()) or scoped_ids
        if not emp_ids and self.department_ids:
            dept_dom = [
                ("company_id", "in", self.company_ids.ids),
                ("department_id", "in", self.department_ids.ids),
            ]
            dept_dom += self._report_hr_employee_domain()
            emp_ids = self.env["hr.employee"].search(dept_dom).ids
        cols = [("employee", "Employee")]
        # Short locale-aware headers for PDF/XLSX; keys stay ISO strings for row dicts.
        cols += [(str(day), format_date(self.env, day, date_format="short")) for day in days]
        rows = []
        for eid in emp_ids or [0]:
            emp = self.env["hr.employee"].browse(eid)
            if not emp:
                continue
            if scoped_ids and emp.id not in scoped_ids:
                continue
            line = {"employee": emp.display_name}
            for day in days:
                line[str(day)] = round(by_emp_day[eid].get(day, 0.0), 2)
            rows.append(line)
        return {
            "title": "Attendance matrix (worked hours)",
            "filename": "in_att_monthly_matrix",
            "sheet_name": "matrix",
            "columns": cols,
            "rows": rows,
        }

    def _att_domain(self):
        end = self.date_to + timedelta(days=1)
        dom = [
            ("check_in", ">=", fields.Datetime.to_datetime(self.date_from)),
            ("check_in", "<", fields.Datetime.to_datetime(end)),
            ("employee_id.company_id", "in", self.company_ids.ids),
        ]
        if self.department_ids:
            dom.append(("employee_id.department_id", "in", self.department_ids.ids))
        dom += self._report_employee_domain()
        return dom


class HrInReportWizardAttExceptions(models.TransientModel):
    _name = "hr.in.report.wizard.att.exceptions"
    _description = "Attendance exceptions (missing check-out)"
    _inherit = ["hr.in.report.wizard.mixin"]

    def _pdf_report_xmlid(self):
        return "IndiaHrReports.action_report_att_exceptions"

    def _professional_pdf_sum_column_keys(self):
        return ["worked_hours"]

    def _get_dataset(self):
        self.ensure_one()
        end = self.date_to + timedelta(days=1)
        dom = [
            ("check_in", ">=", fields.Datetime.to_datetime(self.date_from)),
            ("check_in", "<", fields.Datetime.to_datetime(end)),
            ("employee_id.company_id", "in", self.company_ids.ids),
            ("check_out", "=", False),
        ]
        if self.department_ids:
            dom.append(("employee_id.department_id", "in", self.department_ids.ids))
        dom += self._report_employee_domain()
        Att = self.env["hr.attendance"].search(dom, order="check_in")
        self._enforce_row_cap(len(Att))
        cols = [
            ("employee", "Employee"),
            ("department", "Department"),
            ("check_in", "Check in"),
            ("worked_hours", "Worked hours"),
        ]
        rows = [
            {
                "employee": a.employee_id.display_name,
                "department": a.employee_id.department_id.name or "",
                "check_in": a.check_in,
                "worked_hours": a.worked_hours,
            }
            for a in Att
        ]
        return {
            "title": "Attendance exceptions (open punches)",
            "filename": "in_att_exceptions",
            "sheet_name": "exceptions",
            "columns": cols,
            "rows": rows,
        }


class HrInReportWizardAttOvertime(models.TransientModel):
    _name = "hr.in.report.wizard.att.ot"
    _description = "Overtime summary"
    _inherit = ["hr.in.report.wizard.mixin"]

    daily_threshold = fields.Float(string="Regular hours / day", default=8.0)

    def _pdf_report_xmlid(self):
        return "IndiaHrReports.action_report_att_ot"

    def _professional_pdf_sum_column_keys(self):
        return ["ot_hours"]

    def _att_domain(self):
        end = self.date_to + timedelta(days=1)
        dom = [
            ("check_in", ">=", fields.Datetime.to_datetime(self.date_from)),
            ("check_in", "<", fields.Datetime.to_datetime(end)),
            ("employee_id.company_id", "in", self.company_ids.ids),
        ]
        if self.department_ids:
            dom.append(("employee_id.department_id", "in", self.department_ids.ids))
        dom += self._report_employee_domain()
        return dom

    def _get_dataset(self):
        self.ensure_one()
        Att = self.env["hr.attendance"].search(self._att_domain())
        self._enforce_row_cap(len(Att))
        ot_by_emp = defaultdict(float)
        for a in Att:
            wh = a.worked_hours or 0.0
            ot_by_emp[a.employee_id.id] += max(0.0, wh - self.daily_threshold)
        cols = [("employee", "Employee"), ("department", "Department"), ("ot_hours", "Overtime hours")]
        rows = []
        for eid, hours in sorted(ot_by_emp.items(), key=lambda x: -x[1]):
            emp = self.env["hr.employee"].browse(eid)
            rows.append(
                {
                    "employee": emp.display_name,
                    "department": emp.department_id.name or "",
                    "ot_hours": round(hours, 2),
                }
            )
        return {
            "title": "Overtime summary",
            "filename": "in_att_overtime_summary",
            "sheet_name": "ot",
            "columns": cols,
            "rows": rows,
        }
