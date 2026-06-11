# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Website(models.Model):
    _inherit = 'website'

    disable_out_of_stock_variant = fields.Boolean(
        string='Disable Out of Stock Product Variant',
        default=False,
        help='When enabled, out-of-stock product variants are disabled on the shop: '
             'they show "This combination does not exist" and the Add to cart button is disabled.',
    )
    hide_out_of_stock_products_from_shop = fields.Boolean(
        string='Hide Out of Stock Products from Shop',
        default=False,
        help='When enabled, products with no available quantity (on hand) are hidden from the shop listing. '
             'Only products with at least one variant in stock (or non-storable products) are shown.',
    )
