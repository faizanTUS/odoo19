# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    product_image_search_enabled = fields.Boolean(
        string='Enable Product Image Search on Website',
        related='company_id.product_image_search_enabled',
        readonly=False,
        help="Enable or disable the product image search feature on the website."
    )