# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    uap_office_preview = fields.Boolean(
        string="Microsoft Office online preview",
        help="Use Microsoft Office Online to embed Word, Excel, and PowerPoint "
        "attachments. Requires a reachable HTTPS base URL for your database.",
        config_parameter="document_attachment_universal_preview.office_preview",
        default=True,
    )
    uap_google_viewer_fallback = fields.Boolean(
        string="Google Docs viewer fallback",
        help="If enabled, tries Google Docs embedded viewer when Office Online "
        "is unavailable. Same public URL requirement; use only if your policy allows.",
        config_parameter="document_attachment_universal_preview.google_viewer_fallback",
        default=False,
    )
