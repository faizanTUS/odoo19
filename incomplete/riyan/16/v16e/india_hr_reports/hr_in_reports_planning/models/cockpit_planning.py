# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import _

from odoo.addons.india_hr_reports.hr_in_reports.models.cockpit_registry import register_cockpit_provider


class PlanningCockpitProvider:
    @staticmethod
    def collect(env, filters):
        return {
            "id": "planning",
            "label": _("Planning"),
            "kpis": [
                {
                    "key": "planning_placeholder",
                    "label": _("Status"),
                    "value": _("Configured"),
                }
            ],
            "charts": [],
        }


register_cockpit_provider("planning", PlanningCockpitProvider)
