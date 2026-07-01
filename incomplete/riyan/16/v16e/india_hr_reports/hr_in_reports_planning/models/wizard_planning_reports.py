# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields, models, _


def _slot_hours(slot):
    """Use Planning allocated hours when defined on the model; else wall-clock span."""
    if "allocated_hours" in slot._fields:
        return float(slot.allocated_hours or 0.0)
    if slot.start_datetime and slot.end_datetime:
        return (slot.end_datetime - slot.start_datetime).total_seconds() / 3600.0
    return 0.0


def _planning_state_label(slot, env):
    if "state" not in slot._fields:
        return ""
    for val, label in slot._fields["state"]._description_selection(env):
        if val == slot.state:
            return label
    return slot.state or ""


class HrInReportWizardPlanCoverage(models.TransientModel):
    _name = "hr.in.report.wizard.plan.coverage"
    _description = "Shift coverage vs demand"
    _inherit = ["hr.in.report.wizard.mixin"]

    def _professional_pdf_sum_column_keys(self):
        return ["hours"]

    def _pdf_report_xmlid(self):
        return "india_hr_reports.action_report_plan_coverage"

    def _slot_domain(self):
        self.ensure_one()
        period_start = fields.Datetime.to_datetime(self.date_from)
        period_end_excl = fields.Datetime.to_datetime(self.date_to + timedelta(days=1))
        dom = [
            "&",
            ("start_datetime", "<", period_end_excl),
            ("end_datetime", ">", period_start),
        ]
        if "company_id" in self.env["planning.slot"]._fields and self.company_ids:
            dom.append(("company_id", "in", self.company_ids.ids))
        dom += self._report_employee_domain()
        if self.department_ids:
            dom.append(("department_id", "in", self.department_ids.ids))
        return dom

    def _get_dataset(self):
        self.ensure_one()
        slots = self.env["planning.slot"].search(self._slot_domain(), order="start_datetime,id")
        self._enforce_row_cap(len(slots))
        cols = [
            ("resource", "Resource"),
            ("employee", "Employee"),
            ("department", "Department"),
            ("role", "Role"),
            ("start", "Start"),
            ("end", "End"),
            ("hours", "Hours"),
            ("state", "Shift status"),
            ("note", "Note"),
        ]
        rows = []
        for s in slots:
            res_name = ""
            if getattr(s, "resource_id", False) and s.resource_id:
                res_name = s.resource_id.name or ""
            emp = ""
            if getattr(s, "employee_id", False) and s.employee_id:
                emp = s.employee_id.display_name
            dept = ""
            if getattr(s, "department_id", False) and s.department_id:
                dept = s.department_id.display_name
            role = s.role_id.name if getattr(s, "role_id", False) and s.role_id else ""
            state = _planning_state_label(s, self.env) if "state" in s._fields else ""
            note = (s.name or "").strip() if getattr(s, "name", False) else ""
            rows.append(
                {
                    "resource": res_name or _("Open / unassigned"),
                    "employee": emp,
                    "department": dept,
                    "role": role,
                    "start": s.start_datetime,
                    "end": s.end_datetime,
                    "hours": round(_slot_hours(s), 2),
                    "state": state,
                    "note": note,
                }
            )
        return {
            "title": "Shift coverage vs demand",
            "filename": "in_plan_shift_coverage",
            "sheet_name": "planning",
            "columns": cols,
            "rows": rows,
        }


class HrInReportWizardPlanUnderOver(models.TransientModel):
    _name = "hr.in.report.wizard.plan.under_over"
    _description = "Under / over planned hours"
    _inherit = ["hr.in.report.wizard.mixin"]

    weekly_capacity_hours = fields.Float(string="Assumed weekly capacity / resource", default=40.0)

    def _professional_pdf_sum_column_keys(self):
        return ["planned_hours", "delta"]

    def _pdf_report_xmlid(self):
        return "india_hr_reports.action_report_plan_under_over"

    def _slot_domain(self):
        self.ensure_one()
        period_start = fields.Datetime.to_datetime(self.date_from)
        period_end_excl = fields.Datetime.to_datetime(self.date_to + timedelta(days=1))
        dom = [
            "&",
            ("start_datetime", "<", period_end_excl),
            ("end_datetime", ">", period_start),
        ]
        if "company_id" in self.env["planning.slot"]._fields and self.company_ids:
            dom.append(("company_id", "in", self.company_ids.ids))
        dom += self._report_employee_domain()
        if self.department_ids:
            dom.append(("department_id", "in", self.department_ids.ids))
        return dom

    def _get_dataset(self):
        self.ensure_one()
        slots = self.env["planning.slot"].search(self._slot_domain())
        self._enforce_row_cap(len(slots))
        by_res = {}
        for s in slots:
            rid = s.resource_id.id if getattr(s, "resource_id", False) and s.resource_id else 0
            hrs = _slot_hours(s)
            by_res[rid] = by_res.get(rid, 0.0) + hrs
        calendar_days = (self.date_to - self.date_from).days + 1
        weeks = max(1.0, calendar_days / 7.0)
        cap = self.weekly_capacity_hours * weeks
        cols = [
            ("resource", "Resource"),
            ("planned_hours", "Planned hours"),
            ("capacity", "Assumed capacity"),
            ("delta", "Under(-) / over(+)"),
        ]
        rows = []
        for rid, planned in sorted(by_res.items(), key=lambda x: (-x[1], x[0])):
            if rid:
                res = self.env["resource.resource"].browse(rid)
                label = res.name or _("Resource #%s") % rid
            else:
                label = _("Open / unassigned shifts")
            rows.append(
                {
                    "resource": label,
                    "planned_hours": round(planned, 2),
                    "capacity": round(cap, 2),
                    "delta": round(planned - cap, 2),
                }
            )
        return {
            "title": "Under / over planned hours",
            "filename": "in_plan_under_over",
            "sheet_name": "planning",
            "columns": cols,
            "rows": rows,
        }
