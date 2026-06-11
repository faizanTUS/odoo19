# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _is_add_to_cart_allowed(self):
        allowed = super()._is_add_to_cart_allowed()
        if not allowed:
            return False

        website = self.env['website'].get_current_website()
        if not website.disable_out_of_stock_variant:
            return allowed

        if self.detailed_type != 'product':
            return allowed

        if self.free_qty < 1:
            return False

        return allowed