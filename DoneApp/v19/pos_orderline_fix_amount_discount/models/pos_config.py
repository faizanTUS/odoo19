# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import fields, models


class POSConfig(models.Model):
    _inherit = 'pos.config'

    fix_discount = fields.Boolean(string="Enable Fix Discount", default=True)
