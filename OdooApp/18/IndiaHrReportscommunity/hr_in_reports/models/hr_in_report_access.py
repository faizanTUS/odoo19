# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
"""Access helpers for HR India reports (groups + employee hierarchy)."""

from odoo import api, models
from odoo.exceptions import AccessError


class HrInReportAccess(models.AbstractModel):
    """Centralized checks for HR Reports security groups and employee scope."""

    _name = "hr.in.report.access"
    _description = "HR India reports access control"

    # -------------------------------------------------------------------------
    # Groups
    # -------------------------------------------------------------------------

    @api.model
    def has_reports_access(self):
        """User may open HR Reports menus, cockpit, and export wizards."""
        user = self.env.user
        if user.has_group("IndiaHrReportscommunity.group_hr_in_reports_user"):
            return True
        if user.has_group("IndiaHrReportscommunity.group_hr_in_reports_manager"):
            return True
        return any(
            user.has_group(g)
            for g in (
                "hr.group_hr_user",
                "hr_payroll.group_hr_payroll_user",
                "hr_recruitment.group_hr_recruitment_user",
                "planning.group_planning_user",
            )
        )

    @api.model
    def is_hrms_manager(self):
        """Full access to all employees and company-wide HR reports."""
        user = self.env.user
        return (
            user.has_group("IndiaHrReportscommunity.group_hr_in_reports_manager")
            or user.has_group("hr.group_hr_manager")
            or user.has_group("hr.group_hr_user")
        )

    @api.model
    def assert_reports_access(self):
        if not self.has_reports_access():
            raise AccessError(
                self.env._(
                    "You do not have access to HR Reports. "
                    "Ask an administrator to assign the HR Reports Employee or HRMS Manager group."
                )
            )

    @api.model
    def assert_hrms_manager(self):
        self.assert_reports_access()
        if not self.is_hrms_manager():
            raise AccessError(
                self.env._(
                    "This report is restricted to HRMS Managers. "
                    "You can only run employee-scoped reports for yourself and your team."
                )
            )

    # -------------------------------------------------------------------------
    # Employee hierarchy (self + all subordinates in the org chart)
    # -------------------------------------------------------------------------

    @api.model
    def _hierarchy_employee_ids(self, root_employee):
        """Return ids for *root* and every employee below them in the manager chain."""
        if not root_employee:
            return []
        Employee = self.env["hr.employee"]
        ids = {root_employee.id}
        frontier = list(root_employee.child_ids.ids)
        while frontier:
            ids.update(frontier)
            frontier = Employee.search([("parent_id", "in", frontier)]).ids
        return list(ids)

    @api.model
    def accessible_employee_ids(self):
        """Employee records the current user may include in HR India reports."""
        if self.is_hrms_manager():
            return []
        employee = self.env.user.employee_id
        if not employee:
            raise AccessError(
                self.env._(
                    "Your user is not linked to an employee. "
                    "HR Reports for team members require an employee profile."
                )
            )
        return self._hierarchy_employee_ids(employee)

    @api.model
    def resolve_employee_ids(self, selected_ids=None):
        """Effective employee ids for a report export.

        HRMS managers: optional explicit selection; empty means no employee filter.
        Other users: intersection with hierarchy; empty selection means full hierarchy.
        """
        selected_ids = list(selected_ids or [])
        if self.is_hrms_manager():
            return selected_ids
        allowed = set(self.accessible_employee_ids())
        if selected_ids:
            extra = set(selected_ids) - allowed
            if extra:
                raise AccessError(
                    self.env._(
                        "You cannot include employees outside your team "
                        "(yourself and employees reporting to you)."
                    )
                )
            return selected_ids
        return list(allowed)

    @api.model
    def report_employee_domain(self, selected_ids=None, field_name="employee_id"):
        """Domain fragment restricting *field_name* to the report employee scope."""
        ids = self.resolve_employee_ids(selected_ids)
        if self.is_hrms_manager() and not ids:
            return []
        if not ids:
            return [(field_name, "=", False)]
        return [(field_name, "in", ids)]

    @api.model
    def cockpit_employee_domain(self, field_name="employee_id"):
        """Hierarchy restriction for cockpit aggregates (no wizard selection)."""
        return self.report_employee_domain([], field_name=field_name)

    @api.model
    def validate_cockpit_filter_employees(self, filters):
        """Reject cockpit filters that reference employees outside the user scope."""
        if self.is_hrms_manager():
            return
        from .cockpit_data import cockpit_int_ids

        eids = cockpit_int_ids(filters or {}, "employee_ids")
        if not eids:
            return
        allowed = set(self.accessible_employee_ids())
        extra = set(eids) - allowed
        if extra:
            raise AccessError(
                self.env._(
                    "You cannot filter the cockpit on employees outside your team."
                )
            )
