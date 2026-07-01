# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import _

from odoo.addons.india_hr_reports.hr_in_reports.models.cockpit_data import (
    cockpit_company_ids,
    cockpit_date_range,
    cockpit_hr_filters_payslip_domain,
    cockpit_payslip_overlap_domain,
)
from odoo.addons.india_hr_reports.hr_in_reports.models.cockpit_registry import register_cockpit_provider
from odoo.addons.india_hr_reports.hr_in_reports_payroll.models.payroll_report_domain import payslip_confirmed_states


class PayrollCockpitProvider:
    @staticmethod
    def collect(env, filters):
        date_from, date_to = cockpit_date_range(env, filters, default_days=30)
        companies = cockpit_company_ids(env, filters)
        Slip = env["hr.payslip"]
        states = payslip_confirmed_states(env)
        dom = cockpit_payslip_overlap_domain(date_from, date_to, companies) + cockpit_hr_filters_payslip_domain(
            filters, env=env
        ) + [
            ("state", "in", states),
        ]
        total = Slip.search_count(dom)
        by_state = Slip.read_group(dom, [], ["state"], lazy=False)
        state_labels = dict(Slip._fields["state"]._description_selection(env))
        labels = []
        counts = []
        for row in sorted(by_state, key=lambda r: r.get("state") or ""):
            code = row.get("state") or ""
            labels.append(state_labels.get(code, code or _("Unknown")))
            counts.append(int(row.get("__count", 0) or 0))

        charts = []
        if labels:
            charts.append(
                {
                    "id": "payroll_by_state",
                    "type": "bar",
                    "title": _("Confirmed payslips by status"),
                    "labels": labels,
                    "datasets": [{"label": _("Payslips"), "data": counts}],
                }
            )

        draft_dom = (
            cockpit_payslip_overlap_domain(date_from, date_to, companies)
            + cockpit_hr_filters_payslip_domain(filters, env=env)
            + [
                ("state", "=", "draft"),
            ]
        )
        draft_count = Slip.search_count(draft_dom)

        return {
            "id": "payroll",
            "label": _("Payroll"),
            "kpis": [
                {
                    "key": "pay_confirmed",
                    "label": _("Confirmed payslips"),
                    "value": total,
                    "hint": _("Validated / paid in period window"),
                },
                {
                    "key": "pay_draft",
                    "label": _("Draft payslips"),
                    "value": draft_count,
                    "hint": _("Overlapping period"),
                },
            ],
            "charts": charts,
        }


register_cockpit_provider("payroll", PayrollCockpitProvider)
