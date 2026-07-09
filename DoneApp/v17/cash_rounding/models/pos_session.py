# -*- coding: utf-8 -*-

from odoo import models, api


class PosSessionExt(models.Model):
    _inherit = 'pos.session'

    def _loader_params_pos_order(self):
        return {'search_params': {'fields': ['rounding_id']}}

    @api.model
    def _pos_ui_models_to_load(self):
        res = super(PosSessionExt, self)._pos_ui_models_to_load()
        if 'account.cash.rounding' not in res:
            res.append('account.cash.rounding')
        return res

    def _loader_params_account_cash_rounding(self):
        return {'search_params': {'domain': []}}
    
    def _get_pos_ui_account_cash_rounding(self, params):
        return self.env['account.cash.rounding'].search_read(**params['search_params'])