# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import fields, models
from odoo.addons.mail.tools.discuss import Store


class Message(models.Model):
    _inherit = 'mail.message'

    def toggle_pin_chatter(self):
        """Toggle the pinned status of a chatter message using the native
        pinned_at field. This extends pin functionality to all models,
        not just discuss.channel."""
        self.ensure_one()
        self.flush_recordset(['pinned_at'])
        new_pinned_at = fields.Datetime.now() if not self.pinned_at else None
        # Use SQL to avoid updating write_date (same pattern as discuss.channel)
        self.env.cr.execute(
            "UPDATE mail_message SET pinned_at=%s WHERE id=%s",
            (new_pinned_at, self.id)
        )
        self.invalidate_recordset(['pinned_at'])
        Store(bus_channel=self.env.user).add(self, "pinned_at").bus_send()
        return True
