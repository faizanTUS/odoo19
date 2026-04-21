# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    bulk_attach_include_chatter = fields.Boolean(
        string="Bulk ZIP: include chatter attachments",
        config_parameter="bulk_attachments_zip.include_chatter",
        default=True,
        help="When enabled, the default in the download wizard includes files from chatter "
        "messages on the selected records.",
    )
    bulk_attach_max_files = fields.Integer(
        string="Bulk ZIP: max files per download",
        config_parameter="bulk_attachments_zip.max_files",
        default=500,
        help="0 = no limit. Protects the server from huge selections.",
    )
    bulk_attach_max_total_mb = fields.Float(
        string="Bulk ZIP: max total size (MB)",
        config_parameter="bulk_attachments_zip.max_total_mb",
        default=200.0,
        help="0 = no limit. Approximate cap on uncompressed attachment bytes.",
    )
