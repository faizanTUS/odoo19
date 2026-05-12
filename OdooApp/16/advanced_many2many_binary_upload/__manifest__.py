# -*- coding: utf-8 -*-
# Part of TechUltra Solutions. See LICENSE file for full copyright and licensing details.
{
    "name": "Drag & Drop Many2many Attachments (ir.attachment)",
    "summary": (
        "Odoo 16 form widget: drag-and-drop bulk upload for many2many ir.attachment fields—"
        "faster documents, PDFs, and images without extra dialogs."
    ),
    "description": """
Drag & Drop Multi File Upload for Many2many Binary Fields (Odoo 16)
====================================================================

Replace repetitive “attach file” clicks with a **modern drag-and-drop zone** on the form
view for **many2many** fields targeting **ir.attachment**. Users can drop multiple files at
once; uploads still flow through Odoo’s native **FileInput** and attachment pipeline.

**Highlights**
------------
* Drag files anywhere on the widget area to queue them on the hidden file input
* **Multi-file** support with the standard Odoo upload and **x2many** save/remove flow
* Reuses the official **web.Many2ManyBinaryField** QWeb template—no duplicate UI markup

**Typical use**
---------------
Sales orders, purchases, CRM, HR, projects—any form using a many2many to **ir.attachment**
with widget ``many2many_binary_drag_and_drop``.

**Search keywords (App Store / SEO)**
-------------------------------------
Odoo 16 file upload, many2many attachment widget, ir.attachment drag and drop,
bulk file upload Odoo, form view document upload, many2many binary field,
Odoo ERP attachments, multi-file upload widget, Odoo web client field extension,
TechUltra Solutions, techultra, document management UX, sale order attachments,
purchase attachments, CRM file upload, HR documents, project files.
    """,
    "version": "16.0.0.0",
    "category": "Web",
    "author": "Techultra Solutions Private Limited",
    "website": "https://www.techultrasolutions.com/",
    "license": "OPL-1",
    "depends": ["web"],
    "assets": {
        "web.assets_backend": [
            "advanced_many2many_binary_upload/static/src/js/field_binary.js",
        ],
    },
    "images": [
        "static/description/main_screen.gif",
    ],
    "currency": "USD",
    "price": 15.24,
    "installable": True,
    "auto_install": False,
    "application": True,
}
