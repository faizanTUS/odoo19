# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class UniversalPreviewController(http.Controller):
    @http.route("/uap/preview/<int:attachment_id>/<string:checksum>", type="http", auth="public")
    def uap_preview(self, attachment_id, checksum, **kwargs):
        attachment = request.env["ir.attachment"].sudo().browse(attachment_id)
        if not attachment.exists() or attachment.type != "binary":
            return request.not_found()
        if not attachment.checksum or attachment.checksum != checksum:
            return request.not_found()

        inline = str(kwargs.get("inline", "")).lower() in ("1", "true", "yes")
        as_text = str(kwargs.get("as_text", "")).lower() in ("1", "true", "yes")
        content_type = "text/plain; charset=utf-8" if as_text else (attachment.mimetype or "application/octet-stream")
        headers = [
            ("Content-Type", content_type),
            ("Content-Disposition", http.content_disposition(attachment.name or "document")),
        ]
        return request.make_response(attachment.raw, headers=headers)
