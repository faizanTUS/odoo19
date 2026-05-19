# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api


class OAuthProviderLinkedin(models.Model):
    _inherit = 'auth.oauth.provider'

    """Adding client_secret field because some apps likes linkedIn are using this value for its API operations """

    client_secret = fields.Char(string='Client Secret', help="Only need LinkedIn, Twitter etc..")
    return_uri = fields.Char(string='Return URI')
