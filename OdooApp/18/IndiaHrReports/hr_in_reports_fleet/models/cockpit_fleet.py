# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo.addons.IndiaHrReports.hr_in_reports.models.cockpit_registry import register_cockpit_provider


class FleetCockpitProvider:
    @staticmethod
    def collect(env, filters):
        return {
            "id": "fleet",
            "label": env._("Fleet"),
            "kpis": [
                {
                    "key": "fleet_placeholder",
                    "label": env._("Status"),
                    "value": env._("Configured"),
                }
            ],
            "charts": [],
        }


register_cockpit_provider("fleet", FleetCockpitProvider)
