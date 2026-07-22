# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
import logging
import shutil
import tempfile
from base64 import b64decode
from os import remove
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class AttachmentZipDownload(http.Controller):
    """Attachment Zip Download"""

    @http.route("/web/attachment/download_zip_file", type="http", auth="user")
    def download_zip_file(self, **kwargs):
        """Download a zip file from an attachment"""
        attachment_ids = kwargs.get("attachment_ids")
        attachment_ids = eval(attachment_ids)
        if len(attachment_ids) == 0:
            return
        if attachment_ids:
            attachment_ids = request.env["ir.attachment"].sudo().browse(attachment_ids)
            with tempfile.TemporaryDirectory() as attachment_temp_dir:
                for attachment in attachment_ids:
                    try:
                        with open(
                            f"{attachment_temp_dir}/{attachment.name}", "wb"
                        ) as af:
                            af.write(b64decode(attachment.datas))
                    except Exception as e:
                        _logger.info(f"{e}")

                shutil.make_archive(attachment_temp_dir, "zip", attachment_temp_dir)
                zip_path = f"{attachment_temp_dir}.zip"
                response = request.make_response(
                    open(zip_path, "rb").read(),
                    headers=[
                        ('Content-Type', 'application/zip'),
                        ('Content-Disposition', 'attachment; filename=attachments.zip')
                    ]
                )
                remove(zip_path)
                shutil.rmtree(attachment_temp_dir, ignore_errors=True)
                return response
