# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo.addons.india_hr_reports.hr_in_reports.models.cockpit_registry import register_cockpit_provider


class RecruitmentCockpitProvider:
    @staticmethod
    def collect(env, filters):
        return {
            "id": "recruitment",
            "label": env._("Recruitment"),
            "kpis": [
                {
                    "key": "recruitment_placeholder",
                    "label": env._("Status"),
                    "value": env._("Configured"),
                }
            ],
            "charts": [],
        }


register_cockpit_provider("recruitment", RecruitmentCockpitProvider)
