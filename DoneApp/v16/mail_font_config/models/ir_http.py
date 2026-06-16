# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super().session_info()
        result['mail_font_family'] = (
            request.env['ir.config_parameter'].sudo().get_param('mail_font_config.font_family', '')
        )
        return result
