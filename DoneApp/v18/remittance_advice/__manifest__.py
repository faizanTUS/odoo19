# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Vendor Remittance Advice | Payment Remittance Report',
    'version': '18.0.0.0',
    'category': 'Accounting',
    'summary': """
    Generate and share detailed remittance advice documents from vendor payments to streamline payment communication and provide clear payment information to vendors.
    Odoo Remittance Advice
    Vendor Payment Remittance
    Payment Advice Report
    Odoo Vendor Payments
    Remittance Advice PDF
    Vendor Payment Report
    Odoo Accounting Report
    Payment Confirmation Email
    Vendor Remittance Report
    Odoo Payment PDF
    Vendor Bill Payment Report
    Remittance Email Attachment
    Odoo Accounting Addon
    Vendor Payment Documentation
    Payment Summary Report
    Odoo Financial Reports
    Vendor Bill Settlement
    Odoo Email Template
    Payment Receipt PDF
    Accounting Remittance Advice
    Vendor Payment Automation
    Odoo Vendor Module
    Payment Report with Signature
    Vendor Communication Tool
    Odoo Payment Workflow
    Vendor Invoice Settlement Report
    Payment Email Automation
    Odoo Accounting Customization
    Vendor Payment Tracking
    Remittance Report for Vendors
    Odoo Accounting PDF Report
    Vendor Finance Report
    Payment Advice Automation
    Odoo Accounting Extension
    Vendor Payment Email Integration
    Remittance Advice Generator
    Odoo Vendor Bill Report
    Payment Record Documentation
    Accounting Email Integration
    Vendor Payment Reporting Tool
    odoo18
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'description': """
    Vendor Remittance Advice | Payment Remittance Report enhances Odoo's vendor payment process by providing a professional remittance advice document that can be generated, printed, and emailed directly from vendor payment records. The module improves payment communication by allowing businesses to share detailed payment information with vendors in a clear and standardized format.
    Odoo Remittance Advice
    Vendor Payment Remittance
    Payment Advice Report
    Odoo Vendor Payments
    Remittance Advice PDF
    Vendor Payment Report
    Odoo Accounting Report
    Payment Confirmation Email
    Vendor Remittance Report
    Odoo Payment PDF
    Vendor Bill Payment Report
    Remittance Email Attachment
    Odoo Accounting Addon
    Vendor Payment Documentation
    Payment Summary Report
    Odoo Financial Reports
    Vendor Bill Settlement
    Odoo Email Template
    Payment Receipt PDF
    Accounting Remittance Advice
    Vendor Payment Automation
    Odoo Vendor Module
    Payment Report with Signature
    Vendor Communication Tool
    Odoo Payment Workflow
    Vendor Invoice Settlement Report
    Payment Email Automation
    Odoo Accounting Customization
    Vendor Payment Tracking
    Remittance Report for Vendors
    Odoo Accounting PDF Report
    Vendor Finance Report
    Payment Advice Automation
    Odoo Accounting Extension
    Vendor Payment Email Integration
    Remittance Advice Generator
    Odoo Vendor Bill Report
    Payment Record Documentation
    Accounting Email Integration
    Vendor Payment Reporting Tool
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
    'depends': ['account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'report/report_remittance_advice_templates.xml',
        'report/remittance_advice_report.xml',
        'data/mail_template_data.xml',
        'views/account_payment_views.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 24.95,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    "application": False,
}
