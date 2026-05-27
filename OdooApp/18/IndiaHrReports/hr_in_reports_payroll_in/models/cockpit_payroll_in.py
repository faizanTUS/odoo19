# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo.addons.IndiaHrReports.hr_in_reports.models.cockpit_registry import register_cockpit_provider


class PayrollIndiaCockpitProvider:
    @staticmethod
    def collect(env, filters):
        return {
            "id": "payroll_in",
            "label": env._("India payroll"),
            "kpis": [
                {
                    "key": "payroll_in_placeholder",
                    "label": env._("Statutory pack"),
                    "value": env._("Skeleton"),
                }
            ],
            "charts": [],
        }


register_cockpit_provider("payroll_in", PayrollIndiaCockpitProvider)
