# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.http import request
import logging
import pytz
from odoo.addons.base.models.res_users import check_identity
import string
from random import choice
import datetime

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    two_fa_enable= fields.Boolean(
        string='Two-Factor Authentication Through Email',
        help='Enable Two-Factor Authentication Through Email for this user.',
        default=False,
    )
    def generate_otp(self, number_of_digits):
        otp = ''.join(choice(string.digits) for _ in range(number_of_digits))
        return otp

    # @classmethod
    # def _login(cls, db, login, password, user_agent_env):
    #     if not password:
    #         raise AccessDenied()
    #     ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
    #
    #     try:
    #         with cls.pool.cursor() as cr:
    #             self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
    #             with self._assert_can_auth():
    #                 user = self.search(self._get_login_domain(login), order=self._get_login_order(), limit=1)
    #                 if not user:
    #                     raise AccessDenied()
    #                 user = user.with_user(user)
    #                 self.env.cr.execute(
    #                     "SELECT COALESCE(password, '') FROM res_users WHERE id=%s",
    #                     [user.id]
    #                 )
    #                 hashed = self.env.cr.fetchone()[0]
    #                 if not password == hashed + 'mobile_otp_login':
    #                     user._check_credentials(password, user_agent_env)
    #
    #                 tz = request.httprequest.cookies.get('tz') if request else None
    #                 if tz in pytz.all_timezones and (not user.tz or not user.login_date):
    #                     # first login or missing tz -> set tz to browser tz
    #                     user.tz = tz
    #                 user._update_last_login()
    #
    #     except AccessDenied:
    #         _logger.info("Login failed for db:%s login:%s from %s", db, login, ip)
    #         raise
    #
    #     _logger.info("Login successful for db:%s login:%s from %s", db, login, ip)
    #
    #     return user.id

    def _mfa_type(self):
        # Call original method first
        r = super()._mfa_type()
        if r is not None:
            return r

        # Email-based TOTP
        if self.two_fa_enable and not request.session.get('login_by_email'):
            return 'totp_email'

    def _mfa_url(self):
        r = super()._mfa_url()
        if r is not None:
            return r

        if self._mfa_type() == 'totp_email':
            return f"/web/login/email-2fa-auth?email={self.login}"

    @check_identity
    def action_enable_two_fa_email_wizard(self):
        if self.env.user != self:
            raise UserError(_("Two-factor authentication can only be enabled for yourself"))

        if self.two_fa_enable:
            raise UserError(_("Two-factor authentication already enabled"))
        email = self.login
        user_name = self.partner_id.name or self.name
        user_id = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
        if user_id:
            otp = self.generate_otp(6)

            # Save OTP to custom model
            request.env['otp.verification'].sudo().create({
                'otp': otp,
                'email': email,
                'create_date_otp': datetime.datetime.now(pytz.utc).replace(tzinfo=None)  # Convert to naive datetime
            })
            # # Send OTP Email using template
            # template = self.env.ref('tus_email_otp_login.email_template_otp_login')
            # # Robust fallback for email_from
            # email_from = (
            #     user_id.company_id.email or
            #     self.env.company.email or
            #     self.env['ir.config_parameter'].sudo().get_param('mail.default.from') or
            #     'notifications@yourdomain.com' # Ultimate fallback to prevent AssertionError
            # )
            # template.with_context(otp=otp, email_to=email, email_from=email_from).sudo().send_mail(
            #     self.id,
            #     email_values={
            #         'auto_delete': True,
            #         'email_from': email_from,
            #         'email_to': email,
            #     },
            #     force_send=True,
            # )
            mail_body = f"""
                            <html>
                            <head>
                              <style>
                                body {{
                                  font-family: Arial, sans-serif;
                                  background-color: #f4f4f4;
                                  margin: 0;
                                  padding: 0;
                                }}
                                .email-container {{
                                  max-width: 600px;
                                  margin: 20px auto;
                                  background-color: #ffffff;
                                  padding: 20px;
                                  border-radius: 10px;
                                  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
                                }}
                                .header {{
                                  background-color: #007bff;
                                  color: white;
                                  text-align: center;
                                  padding: 15px;
                                  font-size: 20px;
                                  font-weight: bold;
                                  border-radius: 10px 10px 0 0;
                                }}
                                .content {{
                                  padding: 20px;
                                  font-size: 16px;
                                  color: #333;
                                  line-height: 1.6;
                                }}
                                .footer {{
                                  text-align: center;
                                  padding: 15px;
                                  font-size: 14px;
                                  color: #777;
                                  background-color: #f9f9f9;
                                  border-radius: 0 0 10px 10px;
                                }}
                                .logo {{
                                  text-align: center;
                                  margin-bottom: 10px;
                                }}
                                .banner {{
                                  text-align: center;
                                  margin-bottom: 20px;
                                }}
                              </style>
                            </head>
                            <body>
                              <div class="email-container">
                                <div class="header">Your One-Time Password (OTP) 🔑</div>
                                <div class="content">
                                  <p>Dear <strong>{user_name}</strong> 👋,</p>
                                  <p>Your One-Time Password (OTP) for login is: <strong style="color: green;">{otp}</strong> 🔑</p>
                                  <p>This OTP is valid for <strong>2 minutes</strong>. Do not share it. ⏰</p>
                                </div>
                                <div class="footer">
                                  Regards,<br>
                                  <strong>{request.env.company.name}</strong><br>
                                  {request.env.company.email} ✅
                                </div>
                              </div>
                            </body>
                            </html>
                            """

            request.env['mail.mail'].sudo().create({
                'subject': _('Your One-Time Password (OTP) for Login'),
                'email_from': user_id.company_id.email or request.env.company.email,
                'author_id': user_id.partner_id.id,
                'email_to': email,
                'body_html': mail_body,
            }).send()

        return {
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_model': 'email.auth.otp.wizard',
            'name': _("Two-Factor Authentication with Email Activation"),
            'views': [(False, 'form')],
            'context': dict(self.env.context, default_email=email, default_user_id=user_id.id),
        }

    @check_identity
    def action_disable_two_fa_email_wizard(self):
        logins = ', '.join(map(repr, self.mapped('login')))
        if not (self == self.env.user or self.env.user._is_admin() or self.env.su):
            _logger.info("2FA disable: REJECT for %s (%s) by uid #%s", self, logins, self.env.user.id)
            return False

        self.revoke_all_devices()
        self.two_fa_enable = False
        _logger.info("2FA for whatsapp disable: SUCCESS for %s (%s) by uid #%s", self, logins, self.env.user.id)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'warning',
                'message': _("Two-factor authentication disabled for the following user(s): %s",
                             ', '.join(self.mapped('name'))),
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

    def _login(self, credential, user_agent_env=None):
        if not credential:
            raise AccessDenied()
        ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
        db = self.env.cr.dbname

        if request.params.get('otp'):
            try:
                with self._assert_can_auth(user=credential['login']):
                    user = self.sudo().search(self._get_login_domain(credential['login']), order=self._get_login_order(), limit=1)
                    if not user:
                        raise AccessDenied()
                    user = user.with_user(user).sudo()
                    self.env.cr.execute(
                        "SELECT COALESCE(password, '') FROM res_users WHERE id=%s",
                        [user.id]
                    )
                    hashed = self.env.cr.fetchone()[0]
                    if not credential['password'] == hashed:
                        auth_info = user._check_credentials(credential, user_agent_env)
                    else:
                        credential.update({"type": "otp"})
                        auth_info = {
                            "uid": user.id,
                            "auth_method": credential["type"],
                            "mfa": "default",
                        }

                    tz = request.httprequest.cookies.get('tz') if request else None
                    if tz in pytz.all_timezones and (not user.tz or not user.login_date):
                        # first login or missing tz -> set tz to browser tz
                        user.tz = tz
                    user._update_last_login()

            except AccessDenied:
                _logger.info("Login failed for db:%s login:%s from %s", db, credential['login'], ip)
                raise

            _logger.info("Login successful for db:%s login:%s from %s", db, credential['login'], ip)

            return auth_info
        else:
            return super()._login(credential, user_agent_env=user_agent_env)
