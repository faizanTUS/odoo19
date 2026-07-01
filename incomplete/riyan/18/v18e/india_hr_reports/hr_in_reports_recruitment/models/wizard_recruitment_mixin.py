# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields, models


class HrInReportWizardRecMixin(models.AbstractModel):
    """Optional job filter + shared applicant domains for recruitment exports."""

    _name = "hr.in.report.wizard.rec.mixin"
    _description = "Recruitment report wizard filters"

    job_ids = fields.Many2many("hr.job", string="Jobs")

    def _applicant_domain_company(self):
        return ["|", ("company_id", "=", False), ("company_id", "in", self.company_ids.ids)]

    def _applicant_domain_created_in_period(self):
        """Applications whose create_date falls in [date_from, date_to] (inclusive days)."""
        self.ensure_one()
        start = fields.Datetime.to_datetime(self.date_from)
        end_excl = fields.Datetime.to_datetime(self.date_to) + timedelta(days=1)
        dom = self._applicant_domain_company() + [
            ("create_date", ">=", start),
            ("create_date", "<", end_excl),
        ]
        if self.job_ids:
            dom.append(("job_id", "in", self.job_ids.ids))
        if self.department_ids:
            dom.append(("department_id", "in", self.department_ids.ids))
        return dom

    def _applicant_domain_closed_in_period(self):
        """Applications with date_closed set and falling in [date_from, date_to] (inclusive days)."""
        self.ensure_one()
        start = fields.Datetime.to_datetime(self.date_from)
        end_excl = fields.Datetime.to_datetime(self.date_to) + timedelta(days=1)
        dom = self._applicant_domain_company() + [
            ("date_closed", "!=", False),
            ("date_closed", ">=", start),
            ("date_closed", "<", end_excl),
        ]
        if self.job_ids:
            dom.append(("job_id", "in", self.job_ids.ids))
        if self.department_ids:
            dom.append(("department_id", "in", self.department_ids.ids))
        return dom
