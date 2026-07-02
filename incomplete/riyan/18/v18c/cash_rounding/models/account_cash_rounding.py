# -*- coding: utf-8 -*-
from odoo import models, api

class AccountCashRoundingExt(models.Model):
    _inherit = 'account.cash.rounding'

    @api.model
    def _load_pos_data_domain(self, data):
        res = super(AccountCashRoundingExt, self)._load_pos_data_domain(data)
        res = [('id', 'in', self.sudo().search([]).ids)]
        return res
