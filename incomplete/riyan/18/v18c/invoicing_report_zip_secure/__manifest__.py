# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': 'Invoices Report ZIP Export with Password Protection',
    'version': '18.0',
    'author': "TechUltra Solutions Private Limited",
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'summary': """This feature allows users to export various invoice-related QWeb reports into a single ZIP file with optional password protection. The process simplifies the secure compilation and storage of documents, such as Customer Invoices, Vendor Bills, Credit Notes, and Payments.
                     QWeb report export
                    Invoice report ZIP export
                    Odoo financial report export
                    Export multiple invoices
                    Password-protected ZIP Odoo
                    Secure report export
                    Batch invoice export
                    Customer invoice ZIP download
                    Vendor bill report export
                    Credit note ZIP export
                    Payment report export Odoo
                    Compressed report download
                    Protected document export
                    Odoo accounting report security
                    Encrypted ZIP report download
                    Export multiple QWeb PDFs
                    Download invoices as ZIP
                    Odoo bulk report export
                    ZIP file with password
                    Secure invoice archive
                    Vendor invoice bundling
                    Financial document packaging
                    Batch QWeb PDF export
                    Export accounting reports Odoo
                    Compressed invoice download
                    Streamlined report export
                    PDF report bundle Odoo
                    Export financial records
                    Odoo QWeb batch export
                    Report bundling wizard
                    Secure export wizard Odoo
                    io.BytesIO for ZIP buffer
                    PDF merge and ZIP Odoo  
    """,
    'description': """ With this functionality, users can effortlessly export and download multiple QWeb reports related to invoices, including Customer Invoices, Vendor Bills, Customer Credit Notes, Vendor Credit Notes, and Payments, into a single ZIP file. Users can choose to apply password protection for enhanced security. This feature streamlines the management of important financial documents, ensuring they are securely stored and easily accessible in a compressed, password-protected format.
                        QWeb report export
                    Invoice report ZIP export
                    Odoo financial report export
                    Export multiple invoices
                    Password-protected ZIP Odoo
                    Secure report export
                    Batch invoice export
                    Customer invoice ZIP download
                    Vendor bill report export
                    Credit note ZIP export
                    Payment report export Odoo
                    Compressed report download
                    Protected document export
                    Odoo accounting report security
                    Encrypted ZIP report download
                    Export multiple QWeb PDFs
                    Download invoices as ZIP
                    Odoo bulk report export
                    ZIP file with password
                    Secure invoice archive
                    Vendor invoice bundling
                    Financial document packaging
                    Batch QWeb PDF export
                    Export accounting reports Odoo
                    Compressed invoice download
                    Streamlined report export
                    PDF report bundle Odoo
                    Export financial records
                    Odoo QWeb batch export
                    Report bundling wizard
                    Secure export wizard Odoo
                    io.BytesIO for ZIP buffer
                    PDF merge and ZIP Odoo
    """,
    'category': 'tool',
    'license': 'OPL-1',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'security/res_groups_view.xml',
        'views/account_move.xml',
        'wizard/export_accounting_wizard.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 13.00,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': True,
}
