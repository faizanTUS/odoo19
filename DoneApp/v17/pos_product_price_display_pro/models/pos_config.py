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

    def _get_pos_ui_pos_config(self, params):
        result = super()._get_pos_ui_pos_config(params)
        for config in result:
            config['display_product_price_on_card'] = self.browse(
                config['id']
            ).display_product_price_on_card
        return result