# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    purchase_discount = fields.Boolean(
        string="Purchase Discounts",
        help="Allow discounts on purchase order lines and enable discount features"
    )

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'tus_purchase_discount_advanced.purchase_discount',
            self.purchase_discount
        )

    @api.model
    def get_values(self):
        res = super().get_values()
        purchase_discount = self.env['ir.config_parameter'].sudo().get_param(
            'tus_purchase_discount_advanced.purchase_discount'
        )
        res.update(purchase_discount=purchase_discount == 'True')
        return res
