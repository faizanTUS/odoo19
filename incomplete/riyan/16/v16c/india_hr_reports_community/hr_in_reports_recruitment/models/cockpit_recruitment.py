# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import _

from odoo.addons.india_hr_reports_community.hr_in_reports.models.cockpit_registry import register_cockpit_provider


class RecruitmentCockpitProvider:
    @staticmethod
    def collect(env, filters):
        return {
            "id": "recruitment",
            "label": _("Recruitment"),
            "kpis": [
                {
                    "key": "recruitment_placeholder",
                    "label": _("Status"),
                    "value": _("Configured"),
                }
            ],
            "charts": [],
        }


register_cockpit_provider("recruitment", RecruitmentCockpitProvider)
