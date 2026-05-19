# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    restriction_qty_available = fields.Float(
        string='On Hand',
        compute='_compute_restriction_stock_qty',
        digits='Product Unit of Measure',
        help='Quantity on hand for this product in the sales order warehouse context.',
    )
    restriction_virtual_available = fields.Float(
        string='Forecast',
        compute='_compute_restriction_stock_qty',
        digits='Product Unit of Measure',
        help='Forecast quantity for this product in the sales order warehouse context.',
    )

    @api.depends(
        'product_id',
        'order_id.warehouse_id',
        'company_id',
        'display_type',
    )
    def _compute_restriction_stock_qty(self):
        for line in self:
            if line.display_type or not line.product_id:
                line.restriction_qty_available = 0.0
                line.restriction_virtual_available = 0.0
                continue
            product = line.product_id
            if line.order_id.warehouse_id:
                product = product.with_context(warehouse_id=line.order_id.warehouse_id.id)
            line.restriction_qty_available = product.qty_available
            line.restriction_virtual_available = product.virtual_available
