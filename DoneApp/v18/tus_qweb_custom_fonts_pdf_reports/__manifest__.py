# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Custom Fonts for QWeb PDF Reports | Font Manager | Odoo Report Branding',
    'version': '18.0.0.0',
    'category': 'Tools',
    'summary': """
    Upload and apply custom font files to QWeb PDF reports directly from Odoo Settings.Easily manage company-specific fonts and apply them through Document Layout without any technical configuration.
    Custom PDF Fonts
    QWeb PDF Custom Font
    Upload Fonts in Odoo
    Odoo PDF Report Font
    Document Layout Font
    Custom Font Manager
    Company-specific Fonts
    PDF Report Typography
    Professional PDF Fonts
    Odoo QWeb Report Fonts
    Multi-company Font Support
    Font Customization Module
    PDF Branding in Odoo
    External Layout Font
    Odoo Document Styling
    Custom Fonts for Invoices
    Fonts for Quotations
    Fonts for Purchase Orders
    Fonts for Delivery Slips
    Manage PDF Fonts
    Font File Upload
    TrueType Font Support
    OpenType Font Support
    WOFF Font Support
    WOFF2 Font Support
    EOT Font Support
    QWeb Report Customization
    Professional Report Design
    Branded PDF Reports
    Odoo Reporting Enhancements
    Custom Typography in Odoo
    PDF Report Layout Settings
    User-friendly Font Manager
    Automated PDF Styling
    Corporate Fonts for Odoo
    External Layout Customization
    Custom Font Application
    Odoo PDF Branding
    Visual Report Customization
    Odoo Document Template Fonts
    odoo18
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'description': """
    This module allows users to upload and apply custom font files to QWeb PDF reports directly from Odoo Settings.Fonts can be managed company-wise and easily selected from the Document Layout configuration.Once configured, the chosen font is automatically applied to all reports using the external layout.It removes the need for technical customizations while ensuring consistent branding and professional-looking documents across all reports.
    Custom PDF Fonts
    QWeb PDF Custom Font
    Upload Fonts in Odoo
    Odoo PDF Report Font
    Document Layout Font
    Custom Font Manager
    Company-specific Fonts
    PDF Report Typography
    Professional PDF Fonts
    Odoo QWeb Report Fonts
    Multi-company Font Support
    Font Customization Module
    PDF Branding in Odoo
    External Layout Font
    Odoo Document Styling
    Custom Fonts for Invoices
    Fonts for Quotations
    Fonts for Purchase Orders
    Fonts for Delivery Slips
    Manage PDF Fonts
    Font File Upload
    TrueType Font Support
    OpenType Font Support
    WOFF Font Support
    WOFF2 Font Support
    EOT Font Support
    QWeb Report Customization
    Professional Report Design
    Branded PDF Reports
    Odoo Reporting Enhancements
    Custom Typography in Odoo
    PDF Report Layout Settings
    User-friendly Font Manager
    Automated PDF Styling
    Corporate Fonts for Odoo
    External Layout Customization
    Custom Font Application
    Odoo PDF Branding
    Visual Report Customization
    Odoo Document Template Fonts
    odoo18
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com/',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/custom_font_file_views.xml',
        'views/res_company_views.xml',
        'views/base_document_layout_views.xml',
        'views/report_templates.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 14.90,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    "application": False,
}
