# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_purchase_discount = fields.Boolean(
        string="Purchase Discounts",
        implied_group='tus_purchase_discount_advanced.group_purchase_discount',
        help="Allow discounts on purchase order lines and enable discount features"
    )
