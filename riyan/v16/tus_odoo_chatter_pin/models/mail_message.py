# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class Message(models.Model):
    _inherit = 'mail.message'

    pinned_at = fields.Datetime(
        string='Pinned At',
        default=False,
    )

    def toggle_pin_chatter(self):
        """Toggle pinned state. Returns True if now pinned, False if unpinned."""
        self.ensure_one()
        _logger.info("[TUS Pin] toggle id=%s res_id=%s model=%s pinned_at=%s",
                     self.id, self.res_id, self.model, self.pinned_at)
        if self.pinned_at:
            self.pinned_at = False
            return False
        else:
            self.pinned_at = fields.Datetime.now()
            return True

    @api.model
    def get_pinned_messages_data(self, res_id, model):
        """Return pinned messages for a given record.
        Uses sudo() to bypass message access rules that would filter results.
        """
        _logger.info("[TUS Pin] get_pinned_messages_data res_id=%s model=%s", res_id, model)

        # Use sudo to bypass mail.message access rules
        messages = self.sudo().search([
            ('res_id', '=', int(res_id)),
            ('model', '=', model),
            ('pinned_at', '!=', False),
        ], order='pinned_at desc')

        _logger.info("[TUS Pin] found %s pinned messages", len(messages))

        result = []
        for msg in messages:
            result.append({
                'id': msg.id,
                'body': msg.body,
                'author_name': msg.author_id.name if msg.author_id else (msg.email_from or 'Unknown'),
                'author_id': msg.author_id.id if msg.author_id else False,
                'pinned_at': fields.Datetime.to_string(msg.pinned_at),
            })
        return result