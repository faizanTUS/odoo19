# -*- coding: utf-8 -*-
from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        info = super().session_info()
        ICP = self.env["ir.config_parameter"].sudo()
        info["uap_office_preview"] = ICP.get_param(
            "document_attachment_universal_preview.office_preview", "True"
        ).lower() in ("1", "true", "yes")
        info["uap_google_office_fallback"] = ICP.get_param(
            "document_attachment_universal_preview.google_viewer_fallback", "False"
        ).lower() in ("1", "true", "yes")
        return info
