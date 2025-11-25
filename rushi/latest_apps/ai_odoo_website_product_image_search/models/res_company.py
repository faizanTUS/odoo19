# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    product_image_search_enabled = fields.Boolean(
        string='Enable Product Image Search on Website',
        default=False,
        help="Enable or disable the product image search feature on the website."
    )