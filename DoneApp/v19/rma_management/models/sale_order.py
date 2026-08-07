# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    rma_count = fields.Integer(string='RMA Count', compute='_compute_rma_count')

    def _compute_rma_count(self):
        for order in self:
            order.rma_count = self.env['customer.rma'].search_count([('sale_order_id', '=', order.id)])

    def action_view_rma(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer RMAs',
            'res_model': 'customer.rma',
            'view_mode': 'list,form',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {'default_sale_order_id': self.id},
        }
