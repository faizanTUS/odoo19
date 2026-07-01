# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    multi_location_ids = fields.One2many('multi.location', 'company_id', string="Multi Locations")