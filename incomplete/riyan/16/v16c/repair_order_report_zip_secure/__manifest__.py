# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': 'Secure Repair Order ZIP Export | Password Protected Repair Reports | Bulk PDF Download',
    'version': '16.0.0.0',
    'author': "TechUltra Solutions Private Limited",
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'summary': """The Repair Order Report ZIP Export with Password Protection feature allows users to easily export and download multiple Repair Order reports in a single ZIP file, secured with a password. This ensures that all repair-related documents are conveniently grouped and protected, enhancing the organization and security of your files.
                Repair order ZIP export
                Repair report export Odoo
                Batch repair order report download
                Export multiple repair reports
                Repair report bundling
                Compressed repair documents
                Repair order PDF export
                Repair order batch printing
                QWeb repair report export
                Password-protected ZIP Odoo
                Secure repair report export
                Encrypted ZIP file export
                Odoo repair report security
                Protected repair order reports
                Repair documents with password
                Secure report sharing Odoo
                ZIP file creation Odoo
                Repair order attachment export
                Odoo repair report automation
                Export repair orders securely
                Password-encrypted repair ZIP
    """,
    'description': """ This feature streamlines the process of managing and exporting Repair Order reports by enabling the generation of a password-protected ZIP file containing multiple documents. Whether dealing with numerous repair orders, this tool simplifies file management by efficiently gathering all QWeb-generated reports into one compressed, secure package. Users can choose to create either password-protected or unprotected ZIP files, providing flexibility in safeguarding sensitive information.
                        Repair order ZIP export
                        Repair report export Odoo
                        Batch repair order report download
                        Export multiple repair reports
                        Repair report bundling
                        Compressed repair documents
                        Repair order PDF export
                        Repair order batch printing
                        QWeb repair report export
                        Password-protected ZIP Odoo
                        Secure repair report export
                        Encrypted ZIP file export
                        Odoo repair report security
                        Protected repair order reports
                        Repair documents with password
                        Secure report sharing Odoo
                        ZIP file creation Odoo
                        Repair order attachment export
                        Odoo repair report automation
                        Export repair orders securely
                        Password-encrypted repair ZIP
    """,
    'category': 'tool',
    'license': 'OPL-1',
    'depends': ['repair'],
    'data': [
        'security/ir.model.access.csv',
        'security/res_groups_view.xml',
        'views/repair.xml',
        'wizard/export_repair_orders_wizard.xml',
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
