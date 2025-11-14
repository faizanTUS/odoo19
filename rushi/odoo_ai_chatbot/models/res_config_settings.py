# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    open_ai_api_key = fields.Char(
        config_parameter="chatbot.open_ai_api_key", string="Open Ai Api Key"
    )
    is_open_ai = fields.Boolean(config_parameter="chatbot.is_open_ai", string="Open Ai")
    is_gemini = fields.Boolean(config_parameter="chatbot.is_gemini", string="Gemini Ai")
    gemini_api_key = fields.Char(
        config_parameter="chatbot.gemini_api_key", string="gemini Api Key"
    )

    @api.onchange("is_open_ai", "is_gemini")
    def _onchange_is_ai(self):
        if self.is_open_ai:
            self.gemini_api_key = ""
        elif self.is_gemini:
            self.open_ai_api_key = ""