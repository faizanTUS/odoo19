# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import http, fields
from odoo.http import request
import requests
import logging

_logger = logging.getLogger(__name__)

class LinkedInAuthController(http.Controller):

    @http.route('/linkedin/auth/callback', type='http', auth='public')
    def linkedin_callback(self, **kwargs):
        code = kwargs.get('code')
        state = kwargs.get('state')

        if not code:
            return "Error: No authorization code provided."

        try:
            provider = request.env.ref('odoo_linkedin.provider_linkedin')
            token_data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': provider.return_uri,
                'client_id': provider.client_id,
                'client_secret': provider.client_secret
            }

            response = requests.post(
                "https://www.linkedin.com/oauth/v2/accessToken",
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

            if response.status_code != 200:
                return f"Error getting token: {response.text}"

            access_token = response.json().get('access_token')
            if not access_token:
                return "Error: Token not found in response."

            user = request.env.user.sudo()
            user.write({
                'linkedin_token': access_token,
                'last_token_generate_date': fields.Date.today()
            })

            return request.redirect('/web')

        except Exception as e:
            _logger.exception("LinkedIn OAuth callback failed.")
            return f"Exception: {str(e)}"
