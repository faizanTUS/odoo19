# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields,api
import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('product_id', 'order_id.pricelist_id')
    def _onchange_product_pricelist(self):
        if self.product_id and self.order_id.pricelist_id:
            cost_price = self.product_id.standard_price
            computed_price = cost_price

            pricing_rule = self.env['product.pricelist.item'].search([
                ('min_cost', '<=', cost_price),
                ('max_cost', '>=', cost_price),
                ('pricelist_id', '=', self.order_id.pricelist_id.id)
            ], order='min_cost ASC', limit=1)

            if pricing_rule:
                computed_price = cost_price * (1 + (pricing_rule.price_markup / 100))

            self.price_unit = computed_price

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('pricelist_id')
    def _onchange_pricelist_id(self):
        """Update all order line prices when the pricelist changes."""
        for line in self.order_line:
            line._onchange_product_pricelist()
