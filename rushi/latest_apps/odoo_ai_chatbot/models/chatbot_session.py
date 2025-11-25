# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import fields, models


class ChatbotSession(models.Model):
    _name = "chatbot.session"
    _description = "chatbot session"

    partner_id = fields.Many2one("res.partner", string="Partner_id")
    name = fields.Char(string="Name")
    history_ids = fields.One2many(
        "chat.history", "chatbot_session_id", string="Chat History"
    )
