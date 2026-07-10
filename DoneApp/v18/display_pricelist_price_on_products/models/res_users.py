# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    display_pricelist_on_product = fields.Boolean(
        string='Display Pricelist on Product',
        default=False,
        help='When enabled, the "Pricelist Price on The Product" section is visible on product '
             'forms. When disabled, this section is hidden for you on all products.',
    )
