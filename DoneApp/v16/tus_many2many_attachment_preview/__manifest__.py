# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    "name": "Smart Attachment Preview Pro with File Size Viewer | Chatter & Many2many Binary Viewer | PDF, Image, Video & Office Viewer",
    "version": "16.0.0.0",
    "category": "Productivity/Documents",
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    "summary": """Preview ir.attachment on many2many binary fields and chatter without downloading: PDF, images, MP4/video, Word, Excel, PowerPoint. Saves time and storage.
    
    tus
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited
    file
    preview
    file size
    size
    file show
    file viewer
    file preview
    attachment preview
    file preview viewer
    document preview module
    pdf preview viewer
    image preview tool
    video preview module
    office document viewer
    word file preview
    excel file preview
    powerpoint preview
    ppt viewer
    docx preview
    xlsx preview
    pdf viewer without download
    inline file preview
    file viewer without download
    attachment viewer
    document viewer tool
    file preview addon
    many2many attachment preview
    binary field preview
    chatter attachment preview
    message attachment viewer
    inline attachment viewer
    preview files in form view
    preview files in chatter
    file size display
    show file size
    attachment file size
    document size viewer
    file info display
    smart attachment viewer
    advanced file preview
    multi format preview
    all file preview tool
    file preview system
    document preview solution
    quick file preview
    instant file viewer
    fast document viewer
    no download file viewer
    embedded file preview
    iframe file viewer
    office online viewer
    google docs viewer integration
    document viewing tool
    file management enhancement
    attachment management tool
    document handling system
    file preview extension
    preview multiple file types
    preview attachments instantly
    user friendly file viewer
    productivity file tool
    workflow file viewer
    business document viewer
    enterprise file preview
    modern attachment viewer
    responsive file viewer
    secure file preview
    token based file access
    file access control
    attachment access control
    file preview security
    lightweight file viewer
    high performance file preview
    file preview optimization
    quick document access
    preview files inside system
    file preview interface
    clean attachment ui
    enhanced attachment experience
    smart document access
    digital file viewer
    online file preview tool
    document preview integration
    preview attachments inline
    advanced attachment system
    Odoo chatter attachment preview
    Odoo many2many binary preview
    Odoo file size display
    Odoo attachment preview
    Odoo file viewer
    Odoo document preview
    Odoo PDF viewer
    Odoo image preview
    Odoo video preview
    Odoo office viewer
    Odoo chatter file preview
    Odoo many2many attachment preview
    Odoo binary field preview
    Odoo file size in chatter
    Odoo file size in attachments
    Odoo document management
    Odoo file preview module
    Odoo apps attachment viewer
    Odoo preview without download
    Odoo UX improvement
    Odoo productivity tools
    Odoo attachment manager
    Odoo office file preview
    Odoo Excel preview
    Odoo Word preview
    Odoo PPT preview
    Odoo smart attachments
    Odoo workflow optimization
    
    """,
    "description": """
Smart Attachment Preview Pro with File Size Viewer | Chatter & Many2many Binary Viewer | PDF, Image, Video & Office Viewer for Odoo 16
========================================

**SEO / product keywords:** Odoo attachment preview, many2many binary preview, PDF viewer,
image preview, video preview MP4, document preview without download, Word Excel PowerPoint
preview, ir.attachment preview, chatter file viewer, productivity, Odoo 16.

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
installation, ``addons_path`` (``odoo16/project``), and ``web.base.url`` setup.

    tus
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited
    file
    preview
    file size
    size
    file show
    file viewer
    file preview
    attachment preview
    file preview viewer
    document preview module
    pdf preview viewer
    image preview tool
    video preview module
    office document viewer
    word file preview
    excel file preview
    powerpoint preview
    ppt viewer
    docx preview
    xlsx preview
    pdf viewer without download
    inline file preview
    file viewer without download
    attachment viewer
    document viewer tool
    file preview addon
    many2many attachment preview
    binary field preview
    chatter attachment preview
    message attachment viewer
    inline attachment viewer
    preview files in form view
    preview files in chatter
    file size display
    show file size
    attachment file size
    document size viewer
    file info display
    smart attachment viewer
    advanced file preview
    multi format preview
    all file preview tool
    file preview system
    document preview solution
    quick file preview
    instant file viewer
    fast document viewer
    no download file viewer
    embedded file preview
    iframe file viewer
    office online viewer
    google docs viewer integration
    document viewing tool
    file management enhancement
    attachment management tool
    document handling system
    file preview extension
    preview multiple file types
    preview attachments instantly
    user friendly file viewer
    productivity file tool
    workflow file viewer
    business document viewer
    enterprise file preview
    modern attachment viewer
    responsive file viewer
    secure file preview
    token based file access
    file access control
    attachment access control
    file preview security
    lightweight file viewer
    high performance file preview
    file preview optimization
    quick document access
    preview files inside system
    file preview interface
    clean attachment ui
    enhanced attachment experience
    smart document access
    digital file viewer
    online file preview tool
    document preview integration
    preview attachments inline
    advanced attachment system
    Odoo chatter attachment preview
    Odoo many2many binary preview
    Odoo file size display
    Odoo attachment preview
    Odoo file viewer
    Odoo document preview
    Odoo PDF viewer
    Odoo image preview
    Odoo video preview
    Odoo office viewer
    Odoo chatter file preview
    Odoo many2many attachment preview
    Odoo binary field preview
    Odoo file size in chatter
    Odoo file size in attachments
    Odoo document management
    Odoo file preview module
    Odoo apps attachment viewer
    Odoo preview without download
    Odoo UX improvement
    Odoo productivity tools
    Odoo attachment manager
    Odoo office file preview
    Odoo Excel preview
    Odoo Word preview
    Odoo PPT preview
    Odoo smart attachments
    Odoo workflow optimization
    """,
    "depends": ["web", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/attachment_preview_example_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "tus_many2many_attachment_preview/static/src/scss/many2many_preview.scss",
            "tus_many2many_attachment_preview/static/src/js/attachment_model_patch.js",
            "tus_many2many_attachment_preview/static/src/js/many2many_binary_preview.js",
            "tus_many2many_attachment_preview/static/src/js/attachment_viewer_patch.js",
            "tus_many2many_attachment_preview/static/src/xml/many2many_binary_preview.xml",
            "tus_many2many_attachment_preview/static/src/xml/attachment_size.xml",
            "tus_many2many_attachment_preview/static/src/xml/attachment_viewer_office.xml",
        ],
    },
    'images': [
        'static/description/main_screen.gif'
    ],
    'price': 39.90,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
