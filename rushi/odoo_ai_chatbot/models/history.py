# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import fields, models

class ChatHistory(models.Model):
    _name = "chat.history"
    _description = "Chat History"

    partner_id = fields.Many2one("res.partner", string="Partner_id")
    chatbot_session_id = fields.Many2one("chatbot.session", string="Chatbot session ")
    user_input = fields.Text(string="User  Input")
    bot_response_json = fields.Json(string="Bot Response")
