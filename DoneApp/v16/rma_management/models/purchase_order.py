from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    rma_count = fields.Integer(string='RMA Count', compute='_compute_rma_count')

    def _compute_rma_count(self):
        for order in self:
            order.rma_count = self.env['supplier.rma'].search_count([('purchase_order_id', '=', order.id)])

    def action_view_rma(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Supplier RMAs',
            'res_model': 'supplier.rma',
            'view_mode': 'list,form',
            'domain': [('purchase_order_id', '=', self.id)],
            'context': {'default_purchase_order_id': self.id},
        }
