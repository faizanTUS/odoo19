# -*- coding: utf-8 -*-
{
    "name": "Universal Document Attachment Preview — PDF, Office, Video",
    "summary": "Preview attachments in Odoo without downloading: Microsoft Word, Excel, PowerPoint, PDF, images, audio, and video from chatter everywhere.",
    "description": """
Universal Attachment & Document Preview for Odoo 16
======================================================

Preview **PDF**, **MS Office** (Word, Excel, PowerPoint), **OpenDocument**, **images**, **video**, and **audio** in the attachment viewer from mail chatter (legacy mail JS architecture).

**Keywords:** attachment preview, document preview, PDF viewer, Office viewer, Odoo 16.
    """,
    "version": "16.0.1.0.0",
    "category": "Productivity/Documents",
    "author": "Custom",
    "website": "",
    "license": "LGPL-3",
    "depends": ["web", "mail"],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "document_attachment_universal_preview/static/src/js/attachment_mail_patch.js",
            "document_attachment_universal_preview/static/src/js/attachment_viewer_component_patch.js",
            "document_attachment_universal_preview/static/src/xml/attachment_viewer_uap.xml",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
