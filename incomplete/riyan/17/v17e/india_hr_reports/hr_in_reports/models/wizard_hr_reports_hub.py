# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import fields, models


def _snapshot_first_contract_date(employee):
    """Earliest contract start as date (Odoo 19 hr.version) or legacy hr.contract.

    Order of preference:
    1. ``_get_first_contract_date`` helper (Odoo 19 core hr).
    2. Minimum of ``version_ids.contract_date_start`` (Odoo 19 employment versions).
    3. ``contract_date_start`` directly on the employee (current version).
    4. Legacy ``contract_ids.date_start`` (older Odoo / hr_contract module).
    """
    if hasattr(employee, "_get_first_contract_date"):
        try:
            return employee._get_first_contract_date() or None
        except Exception:
            pass
    if "version_ids" in employee._fields:
        starts = [
            d for d in employee.sudo().version_ids.mapped("contract_date_start") if d
        ]
        if starts:
            return min(starts)
    if "contract_date_start" in employee._fields:
        return employee.contract_date_start or None
    if "contract_ids" in employee._fields and employee.contract_ids:
        starts = [d for d in employee.contract_ids.mapped("date_start") if d]
        return min(starts) if starts else None
    return None


class HrInReportWizardHubHeadcount(models.TransientModel):
    _name = "hr.in.report.wizard.hub.headcount"
    _description = "Headcount & movement report"
    _inherit = ["hr.in.report.wizard.mixin"]

    include_movement_lines = fields.Boolean(
        string="List hire / exit lines",
        default=True,
        help="If enabled, export lists contract starts, contract ends, and employee departures in the period.",
    )

    def _pdf_report_xmlid(self):
        return "india_hr_reports.action_report_hub_headcount"

    def _professional_pdf_sum_column_keys(self):
        if self.include_movement_lines:
            return []
        return ["value"]

    def _employee_domain(self):
        dom = [("company_id", "in", self.company_ids.ids)]
        if self.department_ids:
            dom.append(("department_id", "in", self.department_ids.ids))
        dom += self._report_hr_employee_domain()
        return dom

    def _active_contract_on(self, employee, on_date):
        """Whether employee has an active contract on on_date (Odoo 19: hr.employee API)."""
        if hasattr(employee, "_is_in_contract"):
            return employee._is_in_contract(on_date)
        # Legacy hr.contract (older Odoo / optional hr_contract app)
        if "hr.contract" in self.env and employee.contract_ids:
            for c in employee.contract_ids.filtered(lambda x: x.state != "cancel"):
                if c.date_start and c.date_start <= on_date and (
                    not c.date_end or c.date_end >= on_date
                ):
                    return True
            return False
        return False

    def _get_dataset(self):
        self.ensure_one()
        Employee = self.env["hr.employee"]
        title = "Headcount & movement"
        emps = Employee.search(self._employee_domain())

        opening = sum(1 for e in emps if self._active_contract_on(e, self.date_from))
        closing = sum(1 for e in emps if self._active_contract_on(e, self.date_to))

        # Odoo 19+: employment contracts are carried on hr.version (no hr.contract in CE).
        if "hr.version" in self.env:
            Version = self.env["hr.version"]
            hire_dom = [
                ("company_id", "in", self.company_ids.ids),
                ("contract_date_start", "!=", False),
                ("contract_date_start", ">=", self.date_from),
                ("contract_date_start", "<=", self.date_to),
            ]
            if self.department_ids:
                hire_dom.append(("employee_id.department_id", "in", self.department_ids.ids))
            hire_dom += self._report_employee_domain()
            hires = Version.search(hire_dom)

            exit_dom = [
                ("company_id", "in", self.company_ids.ids),
                ("contract_date_end", "!=", False),
                ("contract_date_end", ">=", self.date_from),
                ("contract_date_end", "<=", self.date_to),
            ]
            if self.department_ids:
                exit_dom.append(("employee_id.department_id", "in", self.department_ids.ids))
            exit_dom += self._report_employee_domain()
            exits_c = Version.search(exit_dom)
        elif "hr.contract" in self.env:
            Contract = self.env["hr.contract"]
            hire_dom = [
                ("company_id", "in", self.company_ids.ids),
                ("date_start", ">=", self.date_from),
                ("date_start", "<=", self.date_to),
                ("state", "!=", "cancel"),
            ]
            if self.department_ids:
                hire_dom.append(("employee_id.department_id", "in", self.department_ids.ids))
            hire_dom += self._report_employee_domain()
            hires = Contract.search(hire_dom)

            exit_dom = [
                ("company_id", "in", self.company_ids.ids),
                ("date_end", ">=", self.date_from),
                ("date_end", "<=", self.date_to),
            ]
            if self.department_ids:
                exit_dom.append(("employee_id.department_id", "in", self.department_ids.ids))
            exit_dom += self._report_employee_domain()
            exits_c = Contract.search(exit_dom)
        else:
            hires = exits_c = self.env["hr.employee"].browse()

        exits_d = Employee.browse()
        if "departure_date" in Employee._fields:
            dep_dom = self._employee_domain() + [
                ("departure_date", ">=", self.date_from),
                ("departure_date", "<=", self.date_to),
            ]
            exits_d = Employee.search(dep_dom)

        if self.include_movement_lines:
            cols = [
                ("employee", "Employee"),
                ("department", "Department"),
                ("event", "Event"),
                ("event_date", "Date"),
                ("note", "Note"),
            ]
            rows = []
            for c in hires:
                start_d = (
                    c.contract_date_start
                    if c._name == "hr.version"
                    else c.date_start
                )
                rows.append(
                    {
                        "employee": c.employee_id.display_name,
                        "department": c.employee_id.department_id.name or "",
                        "event": "Contract start",
                        "event_date": start_d,
                        "note": c.name or "",
                    }
                )
            for c in exits_c:
                end_d = (
                    c.contract_date_end
                    if c._name == "hr.version"
                    else c.date_end
                )
                rows.append(
                    {
                        "employee": c.employee_id.display_name,
                        "department": c.employee_id.department_id.name or "",
                        "event": "Contract end",
                        "event_date": end_d,
                        "note": c.name or "",
                    }
                )
            for e in exits_d:
                rows.append(
                    {
                        "employee": e.display_name,
                        "department": e.department_id.name or "",
                        "event": "Departure",
                        "event_date": e.departure_date,
                        "note": "",
                    }
                )
            rows.sort(key=lambda r: (r["event_date"] or "", r["employee"]))
            if not rows:
                rows.append(
                    {
                        "employee": "-",
                        "department": "",
                        "event": "No movement rows",
                        "event_date": None,
                        "note": "",
                    }
                )
            return {
                "title": title,
                "filename": "in_hr_headcount_movement",
                "sheet_name": "movement",
                "columns": cols,
                "rows": rows,
            }

        cols = [
            ("metric", "Metric"),
            ("value", "Value"),
        ]
        rows = [
            {"metric": "Opening headcount (active contract on start date)", "value": opening},
            {"metric": "New / restarted contracts (starts in period)", "value": len(hires)},
            {"metric": "Contract ends (in period)", "value": len(exits_c)},
            {"metric": "Employee departures (in period)", "value": len(exits_d)},
            {"metric": "Closing headcount (active contract on end date)", "value": closing},
        ]
        return {
            "title": title,
            "filename": "in_hr_headcount_movement",
            "sheet_name": "summary",
            "columns": cols,
            "rows": rows,
        }


class HrInReportWizardHubSnapshot(models.TransientModel):
    _name = "hr.in.report.wizard.hub.snapshot"
    _description = "Employee master snapshot"
    _inherit = ["hr.in.report.wizard.mixin"]

    def _pdf_report_xmlid(self):
        return "india_hr_reports.action_report_hub_snapshot"

    def _get_dataset(self):
        self.ensure_one()
        domain = [("company_id", "in", self.company_ids.ids)]
        if self.department_ids:
            domain.append(("department_id", "in", self.department_ids.ids))
        domain += self._report_hr_employee_domain()
        emps = self.env["hr.employee"].search(domain, order="department_id,name")
        self._enforce_row_cap(len(emps))
        cols = [
            ("name", "Name"),
            ("identification_id", "Identification No"),
            ("department", "Department"),
            ("job", "Job position"),
            ("work_email", "Work email"),
            ("work_phone", "Work phone"),
            ("company", "Company"),
            ("manager", "Manager"),
            ("coach", "Coach"),
            ("first_contract_date", "First contract date"),
        ]
        rows = []
        for e in emps:
            rows.append(
                {
                    "name": e.name,
                    "identification_id": e.identification_id or "",
                    "department": e.department_id.name or "",
                    "job": e.job_id.name or "",
                    "work_email": e.work_email or "",
                    "work_phone": e.work_phone or "",
                    "company": e.company_id.name or "",
                    "manager": e.parent_id.name or "",
                    "coach": e.coach_id.name if getattr(e, "coach_id", False) else "",
                    "first_contract_date": _snapshot_first_contract_date(e),
                }
            )
        return {
            "title": "Employee master snapshot",
            "filename": "in_hr_employee_snapshot",
            "sheet_name": "employees",
            "columns": cols,
            "rows": rows,
            "xlsx_options": {
                # Character widths tuned for snapshot columns (readable in Excel).
                "column_widths": [28, 18, 24, 28, 34, 16, 22, 24, 22, 18],
                "header_row_height": 28,
                "default_row_height": 18,
            },
        }
