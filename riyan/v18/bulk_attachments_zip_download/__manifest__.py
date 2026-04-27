# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    "name": "Mass Attachment Download (Chatter + Binary Fields) | ZIP Export Tool",
    "version": "18.0.0.0",
    "category": "Productivity",
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    "summary": """Download all attachments from selected list records in one ZIP: CRM, Sales, HR, Project, any model. Preview, chatter files, safe limits.
            
    tus
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited 
    chatter
    binary
    chatter file
    file
    file to zip
    zip
    bulk
    attachment download
    bulk attachment download
    download attachments any model
    universal attachment downloader
    mass download files
    download attachments zip
    export attachments bulk
    multi model file download
    download files any module
    global attachment export
    multiple file download
    attachment export tool
    document download zip
    bulk file export
    download documents in zip
    mass attachment exporter
    file downloader tool
    zip attachment download
    record attachment export
    multi record file download
    attachment manager tool
    document export utility
    file compression download
    bulk document exporter
    attachment zip generator
    download all attachments
    multi attachment zip
    file export automation
    attachment extraction tool
    download multiple documents
    mass file downloader
    attachment packaging tool
    document bundle download
    export record attachments
    file archive generator
    download files in bulk
    attachment collection tool
    zip file export module
    multi file export system
    document management export
    attachment batch download
    file grouping download
    export files quickly
    attachment handling tool
    zip download utility
    bulk file management
    record file exporter
    download all documents
    file export wizard
    attachment downloader app
    multi document zip
    file bundle exporter
    document export manager
    download attachments fast
    mass document downloader
    attachment zip creator
    export multiple attachments
    file archive download
    attachment export system
    bulk file utility
    download record files
    document zip tool
    attachment download manager
    file export tool advanced
    zip file attachment exporter
    bulk download manager
    multi file zip exporter
    document batch exporter
    download attachments easily
    file export solution
    attachment bulk tool
    zip multiple files
    export attachments instantly
    file collection exporter
    download all files zip
    attachment export automation
    bulk file zip tool
    document downloader system
    attachment export wizard
    
    """,
    "description": """
Mass Attachment Download (Chatter + Binary Fields) | ZIP Export Tool for Odoo 18
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
CRM documents, sales order files, HR documents, project files, Odoo 18 productivity,
multi attachment download, chatter attachments export.


    tus
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited 
    chatter
    binary
    chatter file
    file
    file to zip
    zip
    bulk
    attachment download
    bulk attachment download
    download attachments any model
    universal attachment downloader
    mass download files
    download attachments zip
    export attachments bulk
    multi model file download
    download files any module
    global attachment export
    multiple file download
    attachment export tool
    document download zip
    bulk file export
    download documents in zip
    mass attachment exporter
    file downloader tool
    zip attachment download
    record attachment export
    multi record file download
    attachment manager tool
    document export utility
    file compression download
    bulk document exporter
    attachment zip generator
    download all attachments
    multi attachment zip
    file export automation
    attachment extraction tool
    download multiple documents
    mass file downloader
    attachment packaging tool
    document bundle download
    export record attachments
    file archive generator
    download files in bulk
    attachment collection tool
    zip file export module
    multi file export system
    document management export
    attachment batch download
    file grouping download
    export files quickly
    attachment handling tool
    zip download utility
    bulk file management
    record file exporter
    download all documents
    file export wizard
    attachment downloader app
    multi document zip
    file bundle exporter
    document export manager
    download attachments fast
    mass document downloader
    attachment zip creator
    export multiple attachments
    file archive download
    attachment export system
    bulk file utility
    download record files
    document zip tool
    attachment download manager
    file export tool advanced
    zip file attachment exporter
    bulk download manager
    multi file zip exporter
    document batch exporter
    download attachments easily
    file export solution
    attachment bulk tool
    zip multiple files
    export attachments instantly
    file collection exporter
    download all files zip
    attachment export automation
    bulk file zip tool
    document downloader system
    attachment export wizard

    """,
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
    'images': [
        'static/description/main_screen.gif'
    ],
    'price': 15.00,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
