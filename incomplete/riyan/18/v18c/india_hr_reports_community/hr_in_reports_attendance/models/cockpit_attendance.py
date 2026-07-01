# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo.addons.india_hr_reports_community.hr_in_reports.models.cockpit_data import (
    cockpit_attendance_company_domain,
    cockpit_attendance_date_range_domain,
    cockpit_attendance_day_groupby,
    cockpit_company_ids,
    cockpit_date_range,
    cockpit_hr_filters_attendance_domain,
)
from odoo.addons.india_hr_reports_community.hr_in_reports.models.cockpit_registry import register_cockpit_provider


class AttendanceCockpitProvider:
    @staticmethod
    def collect(env, filters):
        date_from, date_to = cockpit_date_range(env, filters, default_days=30)
        companies = cockpit_company_ids(env, filters)
        Att = env["hr.attendance"]
        day_groupby = cockpit_attendance_day_groupby(env)
        base_dom = (
            cockpit_attendance_date_range_domain(env, date_from, date_to)
            + cockpit_attendance_company_domain(companies)
            + cockpit_hr_filters_attendance_domain(filters, env=env)
        )
        total_lines = Att.search_count(base_dom)
        open_dom = base_dom + [("check_out", "=", False)]
        open_count = Att.search_count(open_dom) if "check_out" in Att._fields else 0

        day_rows = Att.read_group(base_dom, ['worked_hours:sum'], [day_groupby], orderby=day_groupby, lazy=False)
        count_rows = Att.read_group(base_dom, [], [day_groupby], orderby=day_groupby, lazy=False)

        def _norm_day_key(row):
            k = row.get(day_groupby)
            if isinstance(k, str) and k:
                return k[:10]
            if k:
                return str(k)[:10]
            return ""

        hours_by_day = {_norm_day_key(r): float(r.get("worked_hours", 0) or 0) for r in day_rows}
        count_by_day = {_norm_day_key(r): int(r.get("__count", 0) or 0) for r in count_rows}
        all_days = sorted(set(hours_by_day) | set(count_by_day) - {""})
        labels = []
        hours_series = []
        checkins_series = []
        for d in all_days:
            labels.append(d)
            hours_series.append(round(hours_by_day.get(d, 0.0), 2))
            checkins_series.append(count_by_day.get(d, 0))
        total_hours = sum(hours_series)

        charts = []
        if labels:
            charts.append(
                {
                    "id": "att_hours_by_day",
                    "type": "line",
                    "title": env._("Worked hours by day"),
                    "labels": labels,
                    "datasets": [
                        {
                            "label": env._("Hours"),
                            "data": hours_series,
                            "fill": False,
                        }
                    ],
                }
            )
            charts.append(
                {
                    "id": "att_checkins_by_day",
                    "type": "bar",
                    "title": env._("Check-ins by day"),
                    "labels": labels,
                    "datasets": [
                        {
                            "label": env._("Lines"),
                            "data": checkins_series,
                        }
                    ],
                }
            )

        return {
            "id": "attendance",
            "label": env._("Attendance"),
            "kpis": [
                {
                    "key": "att_lines",
                    "label": env._("Attendance lines"),
                    "value": total_lines,
                    "hint": env._("In selected period"),
                },
                {
                    "key": "att_hours",
                    "label": env._("Worked hours (sum)"),
                    "value": round(total_hours, 2),
                    "hint": env._("Recorded on lines"),
                },
                {
                    "key": "att_open",
                    "label": env._("Open check-ins"),
                    "value": open_count,
                    "hint": env._("No check-out yet"),
                },
            ],
            "charts": charts,
        }


register_cockpit_provider("attendance", AttendanceCockpitProvider)
