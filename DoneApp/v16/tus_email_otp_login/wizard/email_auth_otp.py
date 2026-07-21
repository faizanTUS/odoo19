# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import datetime
import pytz

class EmailAuthOtp(models.TransientModel):
    _name = 'email.auth.otp.wizard'
    _description = 'Email OTP Authentication'

    email = fields.Char(string="Email")
    user_id = fields.Many2one('res.users', string="User")
    otp_code = fields.Char('OTP', size=6)

    #validate the OTP entered by the user
    def verify_otp(self):
        email = self.email
        otp_input = self.otp_code

        res_id = self.env['otp.verification'].search([('email', '=', email)], order="create_date desc", limit=1)
        if not res_id:
            raise UserError("No OTP found for this email.")

        otp_creation_time = res_id.create_date_otp
        if otp_creation_time.tzinfo is None or otp_creation_time.tzinfo.utcoffset(otp_creation_time) is None:
            otp_creation_time = pytz.utc.localize(otp_creation_time)
        time_difference = datetime.datetime.now(pytz.utc) - otp_creation_time
        if time_difference > datetime.timedelta(minutes=2):
            res_id.state = 'rejected'
            raise UserError("OTP has expired.")

        if res_id.otp == otp_input:
            res_id.state = 'verified'
            self.user_id.sudo().search([('login', '=', email)], limit=1).write({
                'two_fa_enable': True,
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'message': _("2-Factor authentication is now enabled."),
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
        raise UserError("Invalid OTP.")
