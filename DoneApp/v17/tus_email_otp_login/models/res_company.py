# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.http import request
import logging
import pytz


class ResUsers(models.Model):
    _inherit = 'res.company'

    email_otp_expire_time = fields.Integer(string='Email OTP Expire Time', default=2)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    email_otp_expire_time = fields.Integer(string='Email OTP Expire Time', related='company_id.email_otp_expire_time',
                                           readonly=False)
