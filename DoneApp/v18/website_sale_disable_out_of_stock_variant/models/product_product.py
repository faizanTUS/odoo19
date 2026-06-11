# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _is_add_to_cart_allowed(self):
        res = super()._is_add_to_cart_allowed()
        if not res:
            return res

        website = self.env['website'].get_current_website()
        if not website.disable_out_of_stock_variant:
            return res

        if not self.is_storable:
            return res

        free_qty = website._get_product_available_qty(self.sudo())
        if free_qty <= 0:
            return False

        return res
