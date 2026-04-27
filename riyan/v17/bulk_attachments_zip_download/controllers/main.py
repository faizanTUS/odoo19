# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import http
from odoo.exceptions import AccessError, UserError, MissingError
from odoo.http import content_disposition, request


class BulkAttachmentsZipController(http.Controller):
    @http.route(
        "/bulk_attachments_zip/download/<int:wizard_id>",
        type="http",
        auth="user",
        readonly=True,
    )
    def download_zip(self, wizard_id, **kwargs):
        wiz = request.env["bulk.attachments.zip.wizard"].browse(wizard_id)
        if not wiz.exists():
            return request.not_found()
        if wiz.create_uid != request.env.user:
            return request.make_response("Forbidden", status=403)
        try:
            buf = wiz._build_zip_stream()
            payload = buf.getvalue()
        except (UserError, AccessError, MissingError) as e:
            msg = e.args[0] if getattr(e, "args", None) else str(e)
            return request.make_response(
                str(msg),
                headers=[("Content-Type", "text/plain; charset=utf-8")],
                status=400,
            )
        fname = wiz._zip_download_filename()
        headers = [
            ("Content-Type", "application/zip"),
            ("Content-Length", len(payload)),
            ("Content-Disposition", content_disposition(fname)),
        ]
        return request.make_response(payload, headers=headers)
