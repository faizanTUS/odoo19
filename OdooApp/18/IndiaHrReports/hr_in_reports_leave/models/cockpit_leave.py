# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo.addons.IndiaHrReports.hr_in_reports.models.cockpit_data import (
    cockpit_company_ids,
    cockpit_date_range,
    cockpit_hr_filters_leave_domain,
    cockpit_leave_overlap_domain,
)
from odoo.addons.IndiaHrReports.hr_in_reports.models.cockpit_registry import register_cockpit_provider


class LeaveCockpitProvider:
    @staticmethod
    def collect(env, filters):
        date_from, date_to = cockpit_date_range(env, filters, default_days=30)
        companies = cockpit_company_ids(env, filters)
        dom = cockpit_leave_overlap_domain(date_from, date_to, companies) + cockpit_hr_filters_leave_domain(
            filters, env=env
        )
        Leave = env["hr.leave"]
        total = Leave.search_count(dom)
        by_state = Leave.read_group(dom, [], ["state"], lazy=False)
        state_labels = dict(env["hr.leave"]._fields["state"]._description_selection(env))
        labels = []
        counts = []
        for row in sorted(by_state, key=lambda r: r.get("state") or ""):
            code = row.get("state") or "unknown"
            labels.append(state_labels.get(code, code))
            counts.append(int(row.get("__count", 0) or 0))

        charts = []
        if labels:
            charts.append(
                {
                    "id": "leave_by_state",
                    "type": "doughnut",
                    "title": env._("Time off by status"),
                    "labels": labels,
                    "datasets": [{"label": env._("Requests"), "data": counts}],
                }
            )

        to_approve = Leave.search_count(dom + [("state", "=", "confirm")])
        approved = Leave.search_count(dom + [("state", "=", "validate")])

        return {
            "id": "leave",
            "label": env._("Time off"),
            "kpis": [
                {
                    "key": "leave_total",
                    "label": env._("Overlapping requests"),
                    "value": total,
                    "hint": env._("Requests touching the period"),
                },
                {
                    "key": "leave_to_approve",
                    "label": env._("To approve"),
                    "value": to_approve,
                },
                {
                    "key": "leave_approved",
                    "label": env._("Approved"),
                    "value": approved,
                },
            ],
            "charts": charts,
        }


register_cockpit_provider("leave", LeaveCockpitProvider)
