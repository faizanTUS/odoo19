# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models

class PosSessionExt(models.Model):
    _inherit = 'pos.session'

    def _loader_params_pos_payment_method(self):
        result = super()._loader_params_pos_payment_method()
        domain = []
        if len(self.config_id.basic_employee_ids) > 0 or len(self.config_id.cashier_ids) > 0:
            domain = ['&', ('company_id', '=', self.config_id.company_id[0].id),
                      '|', '|', ('user_id', '=', self.user_id.id),
                      ('id', 'in', self.config_id.basic_employee_ids.ids + self.config_id.advanced_employee_ids.ids),
                      ('id', 'in', self.config_id.cashier_ids.ids)]
        else:
            domain = [('company_id', '=', self.config_id.company_id[0].id)]
        result['search_params']['domain'] = domain
        result['search_params']['fields'].extend(['name', 'id', 'user_id'])
        return result