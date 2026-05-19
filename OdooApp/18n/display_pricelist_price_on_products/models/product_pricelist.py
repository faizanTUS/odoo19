# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    display_on_product_form = fields.Boolean(
        string='Show on Product Form',
        default=True,
        help='When checked, this pricelist is shown in the "Pricelist Price on The Product" '
             'table on product forms (for users who have "Display pricelist on product" enabled). '
             'Uncheck to hide this pricelist from product forms globally.',
    )
