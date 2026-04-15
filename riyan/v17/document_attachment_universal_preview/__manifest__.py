# -*- coding: utf-8 -*-
{
    "name": "Universal Document Attachment Preview — PDF, Office, Video",
    "summary": "Preview attachments in Odoo without downloading: Microsoft Word, Excel, PowerPoint, PDF, images, audio, and video from chatter everywhere.",
    "description": """
Universal Attachment & Document Preview for Odoo 17
======================================================

Preview **PDF**, **MS Office** (Word, Excel, PowerPoint), **OpenDocument**, **images**, **video**, and **audio** directly in the file viewer modal from mail chatter and anywhere attachments use the standard preview flow.

**Keywords:** attachment preview, document preview, PDF viewer, Office viewer, Excel preview, Word preview, PowerPoint preview, video preview, no download, Odoo 17.
    """,
    "version": "17.0.1.0.0",
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
            "document_attachment_universal_preview/static/src/js/attachment_preview_patch.js",
            "document_attachment_universal_preview/static/src/js/file_viewer_universal_patch.js",
            "document_attachment_universal_preview/static/src/xml/file_viewer_universal.xml",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
