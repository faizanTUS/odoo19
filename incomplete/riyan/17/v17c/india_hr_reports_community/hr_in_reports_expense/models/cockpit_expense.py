from odoo import _
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo.addons.india_hr_reports_community.hr_in_reports.models.cockpit_registry import register_cockpit_provider


class ExpenseCockpitProvider:
    @staticmethod
    def collect(env, filters):
        return {
            "id": "expense",
            "label": _("Expenses"),
            "kpis": [
                {
                    "key": "expense_placeholder",
                    "label": _("Status"),
                    "value": _("Configured"),
                }
            ],
            "charts": [],
        }


register_cockpit_provider("expense", ExpenseCockpitProvider)
