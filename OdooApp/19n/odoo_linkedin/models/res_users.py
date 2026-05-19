# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
import logging

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
    linkedin_token_expiry_date = fields.Date(
        'Token Expiry Date',
        compute='_compute_linkedin_token_expiry_date',
        store=True,
    )

    @api.depends('last_token_generate_date')
    def _compute_linkedin_token_expiry_date(self):
        """Calculate the token expiry date based on the token generation date."""
        for user in self:
            if user.last_token_generate_date:
                expiry_date = fields.Date.from_string(user.last_token_generate_date) + relativedelta(days=50)
                user.linkedin_token_expiry_date = expiry_date
            else:
                user.linkedin_token_expiry_date = False

    def revoke_token(self):
        self.write({
            'linkedin_token': False,
            'last_token_generate_date': False
        })
        return {'type': 'ir.actions.act_window_close'}

    def _remove_expired_token(self):
        date_after_50_days = fields.date.today() - relativedelta(days=50)
        expired_token_users = self.env['res.users'].sudo().search(
            [('last_token_generate_date', '<=', date_after_50_days), ('linkedin_token', 'not in', [False, ''])])
        if expired_token_users:
            expired_token_users.write({'last_token_generate_date': False, 'linkedin_token': False})

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if 'linkedin_username' in vals or 'linkedin_password' in vals:
                rec.write({'linkedin_token': False, 'last_token_generate_date': False})
        return res

    def generate_token(self, **kw):
        """Step 2: Handle LinkedIn OAuth callback"""
        linkedin_credential = {}
        linkedin_auth_provider = self.env.ref('odoo_linkedin.provider_linkedin')
        if linkedin_auth_provider.client_id and linkedin_auth_provider.client_secret and linkedin_auth_provider.return_uri:
            linkedin_credential['api_key'] = linkedin_auth_provider.client_id
            linkedin_credential['secret_key'] = linkedin_auth_provider.client_secret
            linkedin_credential['return_uri'] = linkedin_auth_provider.return_uri
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

        auth_url = (
            "https://www.linkedin.com/oauth/v2/authorization"
            "?response_type=code"
            f"&client_id={linkedin_credential['api_key']}"
            f"&redirect_uri={linkedin_credential['return_uri']}"
            "&scope=r_basicprofile w_member_social"
        )
        return {
            'type': 'ir.actions.act_url',
            'url': auth_url,
            'target': 'new',
        }
