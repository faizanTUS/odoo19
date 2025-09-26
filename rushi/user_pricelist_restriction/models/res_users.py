# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    allowed_pricelist_ids = fields.Many2many(
        'product.pricelist',
        'res_users_pricelist_rel',
        'user_id',
        'pricelist_id',
        string='Allowed Pricelists'
    )
