# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    website_disable_out_of_stock_variant = fields.Boolean(
        string='Disable Out of Stock Product Variant',
        related='website_id.disable_out_of_stock_variant',
        readonly=False,
    )
    website_hide_out_of_stock_products_from_shop = fields.Boolean(
        string='Hide Out of Stock Products from Shop',
        related='website_id.hide_out_of_stock_products_from_shop',
        readonly=False,
    )
