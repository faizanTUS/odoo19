# See LICENSE file for full copyright and licensing details.

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        orders._invalidate_product_restriction_cache()
        return orders

    def write(self, vals):
        res = super().write(vals)
        if 'order_line' in vals:
            self._invalidate_product_restriction_cache()
        return res

    def _invalidate_product_restriction_cache(self):
        self.env.registry.clear_cache()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._invalidate_product_restriction_cache()
        return lines

    def write(self, vals):
        res = super().write(vals)
        if 'product_id' in vals or 'order_id' in vals:
            self._invalidate_product_restriction_cache()
        return res

    def unlink(self):
        res = super().unlink()
        self._invalidate_product_restriction_cache()
        return res

    def _invalidate_product_restriction_cache(self):
        self.env.registry.clear_cache()
