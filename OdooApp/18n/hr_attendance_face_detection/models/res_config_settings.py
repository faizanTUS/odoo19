# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    multi_location_ids = fields.One2many(related='company_id.multi_location_ids', string="Multi Locations",
                                         readonly=False)
