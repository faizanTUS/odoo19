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
        return super(IrAttachment, self).create(vals_list)

    def _get_access_token(self):
        self.ensure_one()
        if not self.access_token:
            token = str(uuid.uuid4())
            self.write({'access_token': token})
            return token
        return self.access_token

    def _to_store(self, store, **kwargs):
        """
        Odoo 18: This method prepares data for the web client store (chatter/discuss).
        We ensure access_token is included in the 'Attachment' data.
        """
        super()._to_store(store, **kwargs)
        for attachment in self:
            # Add access_token to the store data for each attachment
            store.add(attachment, {'access_token': attachment.access_token or attachment._get_access_token()})
