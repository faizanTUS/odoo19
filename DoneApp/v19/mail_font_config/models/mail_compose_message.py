# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
from markupsafe import Markup
from odoo import api, models

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        font_family = (
            self.env['ir.config_parameter'].sudo().get_param('mail_font_config.font_family', '')
        )
        if font_family and defaults.get('body'):
            body = defaults['body']
            body_markup = body if isinstance(body, Markup) else Markup(str(body))
            defaults['body'] = Markup(
                f'<div style="font-family:{font_family};">'
                f'{body_markup}'
                f'</div>'
            )
        return defaults
