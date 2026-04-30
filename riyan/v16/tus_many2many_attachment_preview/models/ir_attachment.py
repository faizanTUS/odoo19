# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import models, api, fields
import uuid


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'access_token' not in vals or not vals['access_token']:
                vals['access_token'] = str(uuid.uuid4())
        return super().create(vals_list)

    def _get_access_token(self):
        self.ensure_one()
        if not self.access_token:
            token = str(uuid.uuid4())
            self.write({'access_token': token})
            return token
        return self.access_token

    def _attachment_format(self, legacy=False):
        """
        Odoo 16: chatter/discuss loads attachments via `_attachment_format()`.
        We inject an access token so Office/Google online viewers can fetch `/web/content`
        without relying on the user's browser session cookies.
        We also inject file_size (in bytes) for display.
        """
        res = super()._attachment_format(legacy=legacy)
        by_id = {att.id: att for att in self}
        for a in res:
            att = by_id.get(a.get("id"))
            if not att:
                continue
            token = att.access_token or att._get_access_token()
            a["accessToken"] = token
            # Expose file_size so the JS can display it
            a["file_size"] = att.file_size
        return res
