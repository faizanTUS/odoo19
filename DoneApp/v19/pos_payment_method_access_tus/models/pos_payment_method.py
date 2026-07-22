# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import fields, models, api
from odoo.osv.expression import AND


class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    user_ids = fields.Many2many("res.users", string="Allowed Users")

    @api.model
    def _load_pos_data_domain(self, data, config):
        domain = ['|', ('active', '=', False), ('active', '=', True)]
        current_user_id = self.env.user.id
        all_methods = self.sudo().search([])
        allowed_ids = [
            m.id for m in all_methods
            if not m.user_ids or current_user_id in m.user_ids.ids
        ]
        return AND([domain, [("id", "in", allowed_ids)]])

    @api.model
    def _load_pos_data_fields(self, config):
        return ['id', 'name', 'is_cash_count', 'use_payment_terminal',
                'split_transactions', 'type', 'image', 'sequence',
                'payment_method_type', 'default_qr', 'user_ids']

    @api.model
    def get_allowed_payment_method_ids(self):
        """RPC method called from JS to get allowed payment method IDs with user_ids map"""
        current_user_id = self.env.user.id
        all_methods = self.sudo().search([])
        result = {}
        for m in all_methods:
            result[m.id] = m.user_ids.ids
        return {
            'current_user_id': current_user_id,
            'user_ids_map': result,
        }