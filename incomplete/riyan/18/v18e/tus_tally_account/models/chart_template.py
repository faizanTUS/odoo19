# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import models
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template(model='account.account')
    def _get_account_account(self, template_code):
        data = super()._get_account_account(template_code)
        # Set tally_wise_reporting=True on Closing Stock (p2123) when loading Indian chart (template_code 'in')
        if template_code == 'in' and 'p2123' in data:
            data['p2123']['tally_wise_reporting'] = True
        return data
