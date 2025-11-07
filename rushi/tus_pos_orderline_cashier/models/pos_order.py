# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import fields, models, api


class PosOrder(models.Model):
    _inherit = "pos.order"

    allow_orderline_user = fields.Boolean(related='session_id.config_id.allow_orderline_user')


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    cashier_id = fields.Many2one('hr.employee', string='Cashier',
                                     help='Cashier who selected in pos')

    orderline_cashier = fields.Char('Cashier Name')
    
    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ['cashier_id']
        params += ['orderline_cashier']
        return params

   