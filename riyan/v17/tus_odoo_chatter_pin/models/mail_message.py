# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import fields, models
# from odoo.addons.mail.tools.discuss import Store


class Message(models.Model):
    _inherit = 'mail.message'

    def toggle_pin_chatter(self):
        self.ensure_one()

        if self.pinned_at:
            self.pinned_at = False
        else:
            self.pinned_at = fields.Datetime.now()

        return True