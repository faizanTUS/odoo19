# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class PosSessionExt(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        res = super(PosSessionExt, self)._pos_ui_models_to_load()
        res = res + ['account.cash.rounding']
        return res

    def _loader_params_account_cash_rounding(self):
        return {
            'search_params': {
                'domain': [('company_id', '=', self.company_id and self.company_id.id or False)],
                'fields': ['name', 'rounding', 'rounding_method'],
            }
        }

    def _get_pos_ui_account_cash_rounding(self, params):
        return self.env['account.cash.rounding'].search_read(**params['search_params'])

