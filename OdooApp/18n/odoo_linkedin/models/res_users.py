from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
import logging
import requests
from urllib.parse import urlsplit
from urllib.parse import parse_qs
import mechanicalsoup

_logger = logging.getLogger(__name__)

try:
    import mechanize
    from linkedin import linkedin
    from urllib.request import HTTPRedirectHandler as MechanizeRedirectHandler

except ImportError:
    _logger.error('Odoo module hr_linkedin_recruitment depends on the several external python package'
                  'Please read the doc/requirement.txt file inside the module.')


class ResUsers(models.Model):
    _inherit = 'res.users'

    linkedin_username = fields.Char('Username')
    linkedin_password = fields.Char('Password')
    linkedin_token = fields.Char('Token')
    last_token_generate_date = fields.Date('Token Generate date')

    def _remove_expired_token(self):
        date_after_50_days = fields.date.today() - relativedelta(days=50)
        expired_token_users = self.env['res.users'].sudo().search(
            [('last_token_generate_date', '<=', date_after_50_days),('linkedin_token','not in',[False,''])])
        if expired_token_users:
            expired_token_users.write({'last_token_generate_date':False,'linkedin_token':False})

    def write(self,vals):
        res = super().write(vals)
        for rec in self:
            if 'linkedin_username' in vals or 'linkedin_password' in vals:
                rec.write({'linkedin_token':False,'last_token_generate_date':False})
        return res
    def generate_token(self):
        self.ensure_one()
        linkedin_credential = {}
        linkedin_auth_provider = self.env.ref('odoo_linkedin.provider_linkedin')
        if linkedin_auth_provider.client_id and linkedin_auth_provider.client_secret:
            linkedin_credential['api_key'] = linkedin_auth_provider.client_id
            linkedin_credential['secret_key'] = linkedin_auth_provider.client_secret
        else:
            raise UserError(_('LinkedIn Access Credentials are empty.Please fill up in Auth Provider form.'))
        if self.linkedin_username:
            linkedin_credential['un'] = self.linkedin_username
        else:
            raise UserError(_('Please fill up Linkedin username User settings.'))
        if self.linkedin_password:
            linkedin_credential['pw'] = self.linkedin_password
        else:
            raise UserError(_('Please fill up Linkedin password in User settings.'))
        # Browser Data Posting And Signing
        br = mechanicalsoup.StatefulBrowser()
        br.set_cookiejar(mechanize.CookieJar())
        return_uri = 'https://www.techultrasolutions.com/'
        linkedin_permissions = ['w_member_social', 'r_basicprofile']
        url = "https://www.linkedin.com/oauth/v2/authorization"
        payload = {
            "response_type": "code",
            "client_id": linkedin_credential['api_key'],
            "redirect_uri": return_uri,
            "state": "DCEeFWf45A53sdfKef424",
            "scope": "r_basicprofile w_member_social"
        }
        try:
            auth = linkedin.LinkedInAuthentication(linkedin_credential['api_key'],
                                                   linkedin_credential['secret_key'],
                                                   return_uri,
                                                   linkedin_permissions)
            response = requests.get(url, params=payload)
            try:
                br.open(response.url)
                br.select_form(selector='form', nr=0)
                br['session_key'] = linkedin_credential['un']
                br['session_password'] = linkedin_credential['pw']
                br.submit_selected()
                # noinspection PyBroadException
                try:
                    # noinspection PyTypeChecker
                    auth.authorization_code = parse_qs(urlsplit(br.get_url()).query)['code']
                    self.write({'last_token_generate_date': fields.date.today(),
                                'linkedin_token': str(auth.get_access_token().access_token)})
                except:
                    br.open(br.get_url())
                    br.select_form(selector='form', nr=1)
                    br.submit_selected()
                    # noinspection PyTypeChecker
                    auth.authorization_code = parse_qs(urlsplit(br.get_url()).query)['code']
                    if not auth.authorization_code:
                        raise UserError("Please check Redirect URLs in the LinkedIn app settings!")
                    self.write({'last_token_generate_date': fields.date.today(),
                                'linkedin_token': str(auth.get_access_token().access_token)})
            except:
                raise UserError("Please check Redirect URLs in the LinkedIn app settings & Configuration!")
        except Exception as e:
            raise UserError(e)
