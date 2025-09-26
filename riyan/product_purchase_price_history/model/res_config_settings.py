# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    purchase_item_limit = fields.Integer("Purchase Item Limit")
    purchase_history_data = fields.Selection([("rfq", "Request for Quotation"), ("purchase", "Purchase Order"), ("both", "Both")],default="both",string="Purchase History Based On",)


class ResConfigSettingsInherit(models.TransientModel):
    _inherit = "res.config.settings"

    purchase_item_limit = fields.Integer(related="company_id.purchase_item_limit",string="Purchase Item Limit",readonly=False)
    purchase_history_data = fields.Selection(readonly=False,related="company_id.purchase_history_data",string="Purchase History Based On")
