# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    display_product_price_on_card = fields.Boolean(
        string='Display Price on Product Cards',
        default=True,
        help='Show product price and tax label (With Tax / Without Tax) on each product card in the POS product grid.',
    )