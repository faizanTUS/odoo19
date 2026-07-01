# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import _

from odoo.addons.india_hr_reports.hr_in_reports.models.cockpit_registry import register_cockpit_provider


class PayrollIndiaCockpitProvider:
    @staticmethod
    def collect(env, filters):
        return {
            "id": "payroll_in",
            "label": _("India payroll"),
            "kpis": [
                {
                    "key": "payroll_in_placeholder",
                    "label": _("Statutory pack"),
                    "value": _("Skeleton"),
                }
            ],
            "charts": [],
        }


register_cockpit_provider("payroll_in", PayrollIndiaCockpitProvider)
