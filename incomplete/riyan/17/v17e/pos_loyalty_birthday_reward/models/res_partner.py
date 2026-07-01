# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    birthdate = fields.Date(string='Birth Date')

    @api.constrains('birthdate')
    def _check_birthdate(self):
        for partner in self:
            if partner.birthdate and partner.birthdate > fields.Date.today():
                raise ValidationError(_("Birth date cannot be in the future."))