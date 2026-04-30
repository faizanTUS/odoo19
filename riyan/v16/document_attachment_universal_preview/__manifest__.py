# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
{
    "name": "Attachment Preview in Odoo | PDF, Word, Excel, PPT Viewer | Universal Attachment Preview",
    "version": "16.0.0.0",
    "category": "Productivity/Documents",
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    "summary": """
    This module provides a unified and user-friendly attachment preview experience across Odoo by enabling in-browser viewing of various file types such as Word, Excel, PowerPoint, images, videos, and audio files. It improves productivity by eliminating the need to download files for quick viewing and supports configuration options for choosing the preview provider.
    attachment file size display
    show file size in Odoo chatter
    document size visibility
    attachment size preview Odoo
    file size tracking
    display attachment details
    chatter file information
    file size indicator in Odoo attachments
    document management features
    attachment metadata display
    file preview in chatter
    attachment preview module
    document preview addon
    preview files without download
    chatter file viewer
    document viewer system
    instant file preview
    universal file preview
    office file preview tool
    spreadsheet preview online
    document viewer integration
    attachment viewer system
    preview docx files online
    preview xlsx files instantly
    preview ppt files in browser
    preview pdf and documents
    preview odt and ods files
    excel file preview tool
    word document preview
    powerpoint preview viewer
    file preview without external apps
    online document preview solution
    quick file access tool
    multi-format file preview
    business document viewer
    smart attachment preview
    seamless file viewing experience
    improve document handling
    document access optimization
    productivity file viewer
    attachment handling improvement
    no download document viewer
    in-app file preview
    modern document preview system
    efficient file preview solution
    cross-format document viewer
    advanced file preview feature
    digital document preview
    fast file preview tool
    secure document preview
    lightweight file viewer module
     """,

    "description": """
    This Odoo module enhances the default attachment viewer by allowing users to preview multiple file formats directly within Odoo—without downloading them.It extends the standard chatter attachment preview system to support not only PDFs and images but also Microsoft Office files, OpenDocument formats, videos, and audio files. The module integrates online document viewers (Microsoft Office Online or Google Docs) to render supported files seamlessly inside a modal viewer.
    attachment file size display
    show file size in Odoo chatter
    document size visibility
    attachment size preview Odoo
    file size tracking
    display attachment details
    chatter file information
    file size indicator in Odoo attachments
    document management features
    attachment metadata display
    file preview in chatter
    attachment preview module
    document preview addon
    preview files without download
    chatter file viewer
    document viewer system
    instant file preview
    universal file preview
    office file preview tool
    spreadsheet preview online
    document viewer integration
    attachment viewer system
    preview docx files online
    preview xlsx files instantly
    preview ppt files in browser
    preview pdf and documents
    preview odt and ods files
    excel file preview tool
    word document preview
    powerpoint preview viewer
    file preview without external apps
    online document preview solution
    quick file access tool
    multi-format file preview
    business document viewer
    smart attachment preview
    seamless file viewing experience
    improve document handling
    document access optimization
    productivity file viewer
    attachment handling improvement
    no download document viewer
    in-app file preview
    modern document preview system
    efficient file preview solution
    cross-format document viewer
    advanced file preview feature
    digital document preview
    fast file preview tool
    secure document preview
    lightweight file viewer module
    """,
    "depends": ["web", "mail"],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "document_attachment_universal_preview/static/src/scss/attachment_list.css",
            "document_attachment_universal_preview/static/src/xml/attachment_list.xml",
            "document_attachment_universal_preview/static/src/js/attachment_size.js",
            "document_attachment_universal_preview/static/src/xml/messaging_attachment_size.xml",
            "document_attachment_universal_preview/static/src/js/attachment_preview_patch.js",
            "document_attachment_universal_preview/static/src/xml/file_viewer_universal.xml",
        ],
    },
    'images': [
        'static/description/main_screen.gif'
    ],
    'price': 34.90,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
