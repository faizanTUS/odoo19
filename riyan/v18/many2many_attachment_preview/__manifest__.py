# -*- coding: utf-8 -*-
{
    "name": "Many2Many Attachment Preview — PDF, Image, Video & Office",
    "summary": "Preview ir.attachment on many2many binary fields and chatter without downloading: PDF, images, MP4/video, Word, Excel, PowerPoint. Saves time and storage.",
    "description": """
Many2Many Attachment Preview for Odoo 18
========================================

**SEO / product keywords:** Odoo attachment preview, many2many binary preview, PDF viewer,
image preview, video preview MP4, document preview without download, Word Excel PowerPoint
preview, ir.attachment preview, chatter file viewer, productivity, Odoo 18.

**What you get**
----------------

* **Many2many** fields using ``widget="many2many_binary"`` gain a **Preview** action (eye
  icon) next to each file—open the same full-screen viewer as in mail chatter.
* **Chatter / Discuss** attachments keep extended preview: extra video/audio MIME types
  and optional **Microsoft Office Online** or **Google Docs** embedding for Office
  documents.
* **PDF** via built-in PDF.js; **images** with zoom and rotate; **video** in the HTML5
  player where the browser allows it.

**Advanced**
------------

* Office viewer toolbar: zoom, reset, open in new tab (when embed is restrictive).
* Settings under **Discuss** to enable or disable online Office preview and to switch
  to Google Docs viewer if policy allows.

See **STEP_BY_STEP_CONFIGURATION.md** (module root) and **doc/CONFIGURATION.rst** for
installation, ``addons_path`` (``odoo18/project``), and ``web.base.url`` setup.
    """,
    "version": "18.0.1.0.5",
    "category": "Productivity/Documents",
    "author": "Custom",
    "website": "https://www.odoo.com",
    "license": "LGPL-3",
    "depends": ["web", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/attachment_preview_example_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "many2many_attachment_preview/static/src/scss/many2many_preview.scss",
            "many2many_attachment_preview/static/src/js/previewable_ir_attachment.js",
            "many2many_attachment_preview/static/src/js/mail_attachment_preview_patch.js",
            "many2many_attachment_preview/static/src/js/many2many_binary_preview.js",
            "many2many_attachment_preview/static/src/js/file_viewer_office_patch.js",
            "many2many_attachment_preview/static/src/xml/many2many_binary_preview.xml",
            "many2many_attachment_preview/static/src/xml/file_viewer_office.xml",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
