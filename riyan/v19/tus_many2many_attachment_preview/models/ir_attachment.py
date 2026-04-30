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
            # Store payload generation can happen in readonly contexts (e.g. webclient boot).
            # Avoid writing in that case; caller can still use the ephemeral token if needed.
            if not self.env.cr.readonly:
                self.write({'access_token': token})
            return token
        return self.access_token

    def _to_store(self, store, fields, **kwargs):
        """
        Odoo 19: This method prepares data for the web client store (chatter/discuss).
        Ensure `access_token` is available client-side for preview/download flows.
        """
        # Odoo 19 doesn't define `ir.attachment._to_store()` upstream, so `Store.add()` would
        # normally fallback to `Store.add_records_fields()`. Keep that behavior, but if another
        # module in the MRO defines `_to_store()`, call it.
        parent_to_store = getattr(super(), "_to_store", None)
        if parent_to_store:
            parent_to_store(store, fields, **kwargs)
        else:
            store.add_records_fields(self, fields)
        # Add fields from inside _to_store() to avoid recursion (store.add() would call _to_store()).
        store.add_records_fields(
            self,
            {'access_token': lambda a: a.access_token or a._get_access_token()},
        )
