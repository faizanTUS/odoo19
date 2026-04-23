# -*- coding: utf-8 -*-
from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        info = super().session_info()
        icp = self.env["ir.config_parameter"].sudo()
        info["map2_office_preview"] = icp.get_param(
            "many2many_attachment_preview.office_online_preview", "True"
        ).lower() in ("1", "true", "yes")
        info["map2_google_viewer_fallback"] = icp.get_param(
            "many2many_attachment_preview.google_docs_viewer", "False"
        ).lower() in ("1", "true", "yes")
        return info
