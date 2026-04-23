# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    map2_office_online_preview = fields.Boolean(
        string="Many2Many / chatter: Office online preview",
        help="Embed Word, Excel, PowerPoint, CSV, RTF, and OpenDocument files using "
        "Microsoft Office Online. Requires a correct public HTTPS web.base.url.",
        config_parameter="many2many_attachment_preview.office_online_preview",
        default=True,
    )
    map2_google_docs_viewer = fields.Boolean(
        string="Use Google Docs viewer for Office files",
        help="Use Google's embedded viewer instead of Microsoft Office Online. "
        "Only enable if your policy allows sending document URLs to Google.",
        config_parameter="many2many_attachment_preview.google_docs_viewer",
        default=False,
    )
