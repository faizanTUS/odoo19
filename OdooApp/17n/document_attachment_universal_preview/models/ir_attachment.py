# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def read(self, fields=None, load="_classic_read"):
        # Mail attachment payload often omits access_token in read fields.
        # Force it into response so external Office viewers can fetch /web/content.
        read_fields = list(fields) if fields else fields
        if read_fields and "access_token" not in read_fields:
            read_fields.append("access_token")

        records = super().read(fields=read_fields, load=load)
        missing_token_ids = [rec["id"] for rec in records if rec.get("id") and not rec.get("access_token")]
        if missing_token_ids:
            for attachment in self.sudo().browse(missing_token_ids):
                attachment.generate_access_token()
            tokens_by_id = {
                att.id: att.access_token for att in self.sudo().browse(missing_token_ids)
            }
            for rec in records:
                rec_id = rec.get("id")
                if rec_id in tokens_by_id and not rec.get("access_token"):
                    rec["access_token"] = tokens_by_id[rec_id]
        return records
