# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from random import choice
import string

from odoo.addons.web.controllers.home import Home, ensure_db
import datetime
from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError

SIGNUP_TEMPLATE = "tus_email_otp_login.custom_otp_signup"
class OtpSignupHome(Home):

    @http.route(website=True)
    def web_auth_signup(self, *args, **kw):
        self.get_auth_signup_qcontext()
        return super(OtpSignupHome, self).web_auth_signup(*args, **kw)

    @http.route('/web/signup/otp', type='http', auth='public', website=True, sitemap=False)
    def web_signup_otp(self, **kw):
        qcontext = request.params.copy()
        if qcontext.get("login") and qcontext.get("password") == qcontext.get("confirm_password"):
            user_id = request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))])
            if user_id:
                qcontext["error"] = _("Another user is already registered using this email address.")
                return request.render(SIGNUP_TEMPLATE, qcontext)

            expiry_time = request.env.company.email_otp_expire_time or 2
            OTP = self.generate_mail_otp(4)
            email = str(qcontext.get('login'))
            name = str(qcontext.get('name'))

            vals = {
                'otp': OTP,
                'email': email,
                'expiry_date': datetime.datetime.now() + datetime.timedelta(minutes=expiry_time),
                'state': 'unverified'
            }

            self.send_signup_mail_otp(name, OTP, email, request.env.company.email)
            request.env['otp.verification'].sudo().create(vals)

            return request.render('tus_email_otp_login.otp_verification_template', {
                'action_url': '/web/signup/otp/verify',
                'submit_button_text': 'Sign Up',
                'context': {
                    'login': email,
                    'name': name,
                    'password': qcontext.get('password'),
                    'confirm_password': qcontext.get('confirm_password'),
                    'expiry_time': expiry_time,
                }
            })
        else:
            qcontext["error"] = _("Passwords do not match, please retype them.")
            return request.render(SIGNUP_TEMPLATE, qcontext)


    def send_signup_mail_otp(self, name, OTP, email, email_from):
        template = request.env.ref('tus_email_otp_login.mail_template_signup_otp')
        if template:
            template.with_context(otp=OTP, name=name).sudo().send_mail(
                request.env.user.partner_id.id,
                email_values={
                    'auto_delete': True,
                    'email_from': email_from,
                    'email_to': email,
                    'message_type': 'user_notification',
                },
                force_send=True,
            )

    @http.route('/web/signup/otp/resend', type='json', auth='public', website=True, sitemap=False)
    def resend_signup_otp(self, **kw):
        """Handle OTP resend requests"""
        email = str(kw.get('login'))
        name = str(kw.get('name'))

        # Generate new OTP
        new_otp = self.generate_mail_otp(4)
        expiry_time = request.env.company.email_otp_expire_time or 2

        # Update or create new OTP record
        vals = {
            'otp': new_otp,
            'email': email,
            'expiry_date': datetime.datetime.now() + datetime.timedelta(minutes=expiry_time),
            'state': 'unverified'
        }

        # Send new OTP
        self.send_signup_mail_otp(name, new_otp, email,email_from=request.env.company.email)

        # Create new OTP verification record
        request.env['otp.verification'].sudo().create(vals)
        return {'resend_otp':'Successful'}

    @http.route('/web/signup/otp/verify', type='http', auth='public', website=True, sitemap=False)
    def web_otp_signup_verify(self, *args, **kw):
        qcontext = request.params.copy()
        email = str(kw.get('login'))
        res_id = request.env['otp.verification'].search([('email', '=', email)], order="create_date desc", limit=1)
        name = str(kw.get('name'))
        password = str(qcontext.get('password'))
        confirm_password = str(qcontext.get('confirm_password'))
        expiry_time = request.env.company.email_otp_expire_time or 2

        try:
            otp = str(kw.get('otp'))
            otp_no = res_id.otp
            if otp_no == otp and res_id.expiry_date > datetime.datetime.now():
                res_id.state = 'verified'
                return self.web_auth_signup(*args, **kw)
            else:
                res_id.state = 'rejected'
                response = request.render("tus_email_otp_login.otp_verification_template", {
                    "action_url": "/web/signup/otp/verify",
                    "resend_url": "/web/signup/otp/resend",
                    "button_label": "Sign Up",
                    "context": {'otp': True, 'otp_login': True,
                                'login': email, 'name': name,
                                'password': password,
                                'confirm_password': confirm_password,
                                'expiry_time': expiry_time,
                                'timer_expired': res_id.expiry_date <= datetime.datetime.now(),
                                }
                })
                return response
        except UserError as e:
            qcontext['error'] = e.name or e.value
            response = request.render("tus_email_otp_login.otp_verification_template", {
                "action_url": "/web/signup/otp/verify",
                "resend_url": "/web/signup/otp/resend",
                "button_label": "Sign Up",
                "context": {'otp': True, 'otp_login': True,
                                  'login': email, 'name': name,
                                  'password': password,
                                  'confirm_password': confirm_password}
            })
        return response

    def generate_mail_otp(self, number_of_digits):
        otp = ''.join(choice(string.digits) for _ in range(number_of_digits))
        return otp
