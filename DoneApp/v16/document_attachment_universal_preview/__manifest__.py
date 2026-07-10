# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
{
    "name": "Attachment Preview in Odoo | PDF, Word, Excel, PPT Viewer | Universal Attachment Preview",
    "version": "16.0.0.0",
    "category": "Productivity/Documents",
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    "summary": """
    Preview a wide range of attachment formats directly in Odoo through a unified in-browser viewer, improving productivity and simplifying document access.
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
    Document Attachment Universal Preview enhances Odoo's standard attachment viewing experience by enabling users to preview a wide range of file formats directly within the system without downloading them. The module extends Odoo's default chatter attachment preview functionality to support business documents, images, multimedia files, and office file formats through a unified in-browser viewing interface.
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
            "document_attachment_universal_preview/static/src/js/attachment_preview_patch.js",
            "document_attachment_universal_preview/static/src/js/file_viewer_universal_patch.js",
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
