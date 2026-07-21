# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from random import choice
import string

from odoo.addons.web.controllers.home import Home, ensure_db
from odoo import http, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.http import request
import datetime
import pytz
import logging
_logger = logging.getLogger(__name__)

TEMPLATE_ID = 'tus_email_otp_login.tus_email_login_template'

class OtpLoginHome(Home):

    @http.route(website=True)
    def web_login(self, redirect=None, **kw):
        ensure_db()
        qcontext = request.params.copy()

        if request.httprequest.method == 'GET':
            otp_dict = {}
            if kw.get("otp_login") and kw.get("otp"):
                otp_dict.update({'otp': True, 'otp_login': True})
                return self.render_tus_email_template(otp_dict)
            if kw.get("otp_login"):
                otp_dict.update({'otp_login': True})
                return self.render_tus_email_template(otp_dict)
            else:
                return super(OtpLoginHome, self).web_login(redirect, **kw)

        # POST handling
        if kw.get('login'):
            request.params['login'] = kw.get('login').strip()
        if kw.get('password') is not None:  # allow empty password (e.g., OTP login)
            request.params['password'] = kw.get('password').strip()

        return super(OtpLoginHome, self).web_login(redirect, **kw)

    def render_tus_email_template(self, otp_dict):
        return request.render(TEMPLATE_ID, otp_dict)

    @http.route('/web/otp/login', type='http', auth='public', website=True, csrf=False)
    def web_otp_login(self, **kw):
        qcontext = request.params.copy()
        email = qcontext.get('login', '').strip()
        user_id = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
        expiry_time = request.env.company.email_otp_expire_time or 2

        if user_id:
            OTP = self.generate_mail_otp(4)
            vals = {
                'otp': OTP,
                'email': email,
                'expiry_date': datetime.datetime.now() + datetime.timedelta(minutes=expiry_time),
                'state': 'unverified'
            }
            self.send_mail_otp(user_id, OTP, email)
            request.env['otp.verification'].sudo().create(vals)

            return request.render('tus_email_otp_login.otp_verification_template', {
                'action_url': '/web/otp/verify',
                'submit_button_text': 'Verify OTP',
                'context': {
                    'login': email,
                    'expiry_time': expiry_time,
                }
            })
        else:
            return request.render(TEMPLATE_ID, {
                'otp': False,
                'otp_login': True,
                'login_error': True,
                'expiry_time': expiry_time,
            })

    @http.route('/web/otp/resend', type='json', auth='public', website=True, csrf=False)
    def web_otp_resend(self, **kw):
        qcontext = request.params.copy()
        email = request.params.copy().get('login', '')

        user_id = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
        expiry_time = request.env.company.email_otp_expire_time or 2

        if user_id:
            OTP = self.generate_mail_otp(4)
            vals = {
                'otp': OTP,
                'email': email,
                'expiry_date': datetime.datetime.now() + datetime.timedelta(minutes=expiry_time),
                'state': 'unverified'
            }
            self.send_mail_otp(user_id, OTP, email)
            request.env['otp.verification'].sudo().create(vals)
            return {'resend_otp': 'Successful', 'expiry_time': expiry_time}
        else:
            response = request.render(TEMPLATE_ID, {
                'otp': False,
                'otp_login': True,
                'login_error': True,
                'expiry_time':expiry_time,
            })
            return response

    def send_mail_otp(self, user_id, OTP, email):
        template = request.env.ref('tus_email_otp_login.email_template_otp_login')
        template.with_context(otp=OTP).sudo().send_mail(
            user_id.id,
            email_values={
                'auto_delete': True,
                'email_from': user_id.company_id.email,
                'email_to': email,
                'message_type': 'user_notification',
            },
            force_send=True,
        )

    #
    # @http.route('/web/otp/verify', type='http', auth='public', website=True, csrf=False)
    # def web_otp_verify(self, *args, **kw):
    #     qcontext = request.params.copy()
    #     email = str(kw.get('login'))
    #     res_id = request.env['otp.verification'].search([('email', '=', email)], order="create_date desc", limit=1)
    #     expiry_time = request.env.company.email_otp_expire_time or 2
    #
    #     try:
    #         otp = str(kw.get('otp'))
    #         otp_no = res_id.otp
    #         if otp_no == otp and res_id.expiry_date > datetime.datetime.now():
    #             res_id.state = 'verified'
    #             user_id = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
    #             request.env.cr.execute(
    #                 "SELECT COALESCE(password, '') FROM res_users WHERE id=%s",
    #                 [user_id.id]
    #             )
    #             hashed = request.env.cr.fetchone()[0]
    #             qcontext.update({'login': user_id.sudo().login,
    #                              'name': user_id.sudo().partner_id.name,
    #                              'password': hashed})
    #             request.params.update(qcontext)
    #             return self.web_login(*args, **kw)
    #         else:
    #             res_id.state = 'rejected'
    #             response = request.render("tus_email_otp_login.otp_verification_template", {
    #                 "action_url": "/web/otp/verify",
    #                 "resend_url": "/web/otp/resend",
    #                 "submit_button_text": "Verify OTP",
    #                 "context": {
    #                     'otp': True, 'otp_login': True,
    #                     'login': email,'otp_invalid':True,
    #                     'timer_expired': res_id.expiry_date <= datetime.datetime.now(),
    #                     'expiry_time': expiry_time,
    #                 }
    #             })
    #
    #             return response
    #     except UserError as e:
    #         qcontext['error'] = e.name or e.value
    #     response = request.render("tus_email_otp_login.otp_verification_template", {
    #         "action_url": "/web/otp/verify",
    #         "resend_url": "/web/otp/resend",
    #         "submit_button_text": "Verify OTP",
    #         "context": {
    #             'otp': True, 'otp_login': True,
    #             'login': email,
    #             'error': qcontext['error'],
    #             'expiry_time': expiry_time,
    #         }
    #     })
    #
    #     return response

    @http.route('/web/otp/verify', type='http', auth='public', website=True, csrf=False)
    def web_otp_verify(self, **kw):
        email = (kw.get('login') or '').strip()
        otp_input = (kw.get('otp') or '').strip()

        expiry_time = request.env.company.email_otp_expire_time or 2

        otp_rec = request.env['otp.verification'].sudo().search(
            [('email', '=', email)],
            order="create_date desc",
            limit=1
        )

        # ❌ No OTP record
        if not otp_rec:
            return self._render_otp_page(email, expiry_time, otp_invalid=True)

        # ⏰ Expired
        if otp_rec.expiry_date <= datetime.datetime.now():
            otp_rec.state = 'rejected'
            return self._render_otp_page(
                email, expiry_time,
                otp_invalid=True,
                timer_expired=True
            )

        # ❌ Wrong OTP
        if otp_rec.otp != otp_input:
            otp_rec.state = 'rejected'
            return self._render_otp_page(email, expiry_time, otp_invalid=True)

        # ✅ OTP VERIFIED
        otp_rec.state = 'verified'

        user = request.env['res.users'].sudo().search(
            [('login', '=', email)],
            limit=1
        )
        if not user:
            return self._render_otp_page(email, expiry_time, otp_invalid=True)

        # 🔐 Mark OTP login
        request.session['login_by_otp'] = True

        try:
            # ✅ THIS IS THE REAL LOGIN
            auth_info = request.session.authenticate(
                request.db,
                {
                    'login': user.login,
                    'password': '__otp__',  # dummy, bypassed in _login
                }
            )
        except AccessDenied:
            return self._render_otp_page(email, expiry_time, otp_invalid=True)

        # 🧹 Cleanup flag
        request.session.pop('login_by_otp', None)

        _logger.info("OTP login successful for %s", user.login)

        # 🚀 Redirect after successful login
        return request.redirect('/web')

    # --------------------------------------------------
    # Helper
    # --------------------------------------------------
    def _render_otp_page(self, email, expiry_time, otp_invalid=False, timer_expired=False):
        return request.render(
            "tus_email_otp_login.otp_verification_template",
            {
                "action_url": "/web/otp/verify",
                "resend_url": "/web/otp/resend",
                "submit_button_text": "Verify OTP",
                "context": {
                    "otp": True,
                    "otp_login": True,
                    "login": email,
                    "otp_invalid": otp_invalid,
                    "timer_expired": timer_expired,
                    "expiry_time": expiry_time,
                }
            }
        )

    # # work below but have bug
    # @http.route('/web/otp/verify', type='http', auth='public', website=True, csrf=False)
    # def web_otp_verify(self, **kw):
    #     email = kw.get('login')
    #     otp = kw.get('otp')
    #
    #     record = request.env['otp.verification'].sudo().search(
    #         [('email', '=', email)],
    #         order="create_date desc",
    #         limit=1
    #     )
    #
    #     if not record:
    #         return request.redirect('/web/login')
    #
    #     if record.otp == otp and record.expiry_date > datetime.datetime.now():
    #         record.state = 'verified'
    #
    #         user = request.env['res.users'].sudo().search(
    #             [('login', '=', email)], limit=1
    #         )
    #         if not user:
    #             raise AccessDenied()
    #
    #         # ✅ Mark session as OTP login
    #         request.session['login_by_otp'] = True
    #
    #         # ✅ Trigger standard login flow
    #         request.params.update({
    #             'login': user.login,
    #             'password': '__otp_login__',  # dummy value
    #         })
    #
    #         _logger.info("OTP verified, proceeding to login for %s", email)
    #         return self.web_login()
    #
    #     record.state = 'rejected'
    #     return request.redirect('/web/login?otp_error=1')

    def generate_mail_otp(self, number_of_digits):
        otp = ''.join(choice(string.digits) for _ in range(number_of_digits))
        return otp

    @http.route('/web/login/email-2fa-auth', type='http', auth='public', website=True)
    def email_2fa_auth(self, **kw):
        email = kw.get('email') or request.session.get('email')
        if not email:
            return request.redirect('/web/login')

        user_id = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)

        # Skip 2FA if disabled
        if not user_id or not user_id.two_fa_enable:
            return self.web_login(redirect=None, **kw)

        expiry_time = request.env.company.email_otp_expire_time or 2
        OTP = self.generate_mail_otp(4)
        self.send_mail_otp(user_id, OTP, email)
        request.session['expected_otp'] = OTP
        request.session['otp_expiry'] = (
                datetime.datetime.now() + datetime.timedelta(minutes=expiry_time)
        ).isoformat()
        request.session['email'] = email

        return request.render('tus_email_otp_login.otp_verification_template', {
            'action_url': '/web/login/email-2fa-submit',
            'submit_button_text': 'Verify OTP',
            'context': {
                'login': email,
                'expiry_time': expiry_time,
            }
        })

    @http.route('/web/login/email-2fa-submit', type='http', auth='public', methods=['POST'], website=True)
    def email_2fa_submit(self, otp=None, redirect=None, **kw):
        email = request.session.get('email')
        user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)

        # If 2FA is disabled for this user, skip verification
        if not user or not user.two_fa_enable:
            return self.web_login(redirect=redirect, **kw)

        expected_otp = request.session.get('expected_otp')
        otp_expiry = request.session.get('otp_expiry')
        now = datetime.datetime.now()

        if not expected_otp or not otp_expiry or not email:
            return request.redirect('/web/login/email-2fa-auth?error=session')

        if now > datetime.datetime.fromisoformat(otp_expiry):
            return request.redirect('/web/login/email-2fa-auth?error=expired')

        if otp == expected_otp:
            request.session.finalize(request.env)
            request.update_env(user=request.session.uid)
            request.update_context(**request.session.context)
            request.session.touch()
            return request.redirect(self._login_redirect(request.session.uid, redirect=redirect))

        return request.redirect('/web/login/email-2fa-auth?error=invalid')
