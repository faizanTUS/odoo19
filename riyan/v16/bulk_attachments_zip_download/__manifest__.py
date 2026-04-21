# -*- coding: utf-8 -*-
{
    "name": "Bulk Attachments ZIP Download — Mass Documents CRM Sales HR",
    "summary": "Download all attachments from selected list records in one ZIP: CRM, Sales, HR, Project, any model. Preview, chatter files, safe limits.",
    "description": """
Bulk Attachments ZIP Download for Odoo 16
=========================================

**Boost productivity** by bundling many documents into a **single ZIP** instead of downloading files one by one from the chatter or attachment panels.

Ideal for **CRM**, **Sales** (quotations & orders), **HR**, **Project**, **Accounting**, and **any custom model** that stores ``ir.attachments`` on records.

Key benefits
------------
* **List view workflow:** select one or many rows → **Actions** → **Download all files**
* **Preview before download:** filenames, MIME type, size; remove lines you do not need
* **Chatter-aware:** optionally include files posted on the **chatter** of selected records
* **Predictable archive name:** ``{technical_model}_attachments.zip`` (e.g. ``sale.order_attachments.zip``)
* **Server-friendly:** configurable **max file count** and **max total size** (MB)
* **Access rules:** only attachments the user can read are included

SEO / keywords
--------------
bulk download attachments, mass document download, ZIP export, list view attachments,
CRM documents, sales order files, HR documents, project files, Odoo 16 productivity,
multi attachment download, chatter attachments export.
    """,
    "version": "16.0.1.0.0",
    "category": "Productivity/Documents",
    "author": "Your Company",
    "website": "https://www.odoo.com",
    "license": "LGPL-3",
    "depends": ["web", "mail", "base_setup"],
    "data": [
        "security/ir.model.access.csv",
        "views/bulk_attachments_zip_wizard_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "bulk_attachments_zip_download/static/src/js/list_controller_bulk_zip.js",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
