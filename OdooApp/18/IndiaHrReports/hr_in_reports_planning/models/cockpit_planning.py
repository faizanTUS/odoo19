# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo.addons.IndiaHrReports.hr_in_reports.models.cockpit_registry import register_cockpit_provider


class PlanningCockpitProvider:
    @staticmethod
    def collect(env, filters):
        return {
            "id": "planning",
            "label": env._("Planning"),
            "kpis": [
                {
                    "key": "planning_placeholder",
                    "label": env._("Status"),
                    "value": env._("Configured"),
                }
            ],
            "charts": [],
        }


register_cockpit_provider("planning", PlanningCockpitProvider)
