# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_display_product_price_on_card = fields.Boolean(
        related='pos_config_id.display_product_price_on_card',
        readonly=False,
    )
