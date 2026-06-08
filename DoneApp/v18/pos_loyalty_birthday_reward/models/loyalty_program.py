# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api, _

class LoyaltyProgram(models.Model):
    _inherit = 'loyalty.program'

    is_birthday_program = fields.Boolean(
        string='Birthday Reward Program',
        help='Enable this for birthday reward programs'
    )