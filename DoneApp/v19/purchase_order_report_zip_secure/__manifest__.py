# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': 'Secure Purchase Order ZIP Export | Password Protected PO Reports | Bulk PDF Download',
    'version': '19.0.0.0',
    'author': "TechUltra Solutions Private Limited",
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'summary': """Exporting Purchase Orders Reports with ZIP Password Protection
                    Purchase order ZIP export
                    Export purchase reports Odoo
                    Purchase order report bundling
                    Password-protected ZIP Odoo
                    Secure PO report download
                    Batch purchase order export
                    Compressed purchase order reports
                    Export multiple purchase PDFs
                    Purchase report encryption
                    Download PO ZIP file Odoo
                    Encrypted ZIP purchase report
                    PO report password protection
                    Secure purchase document export
                    Odoo purchase report security
                    Protected ZIP file generation
                    Report compression with password
                    Secure supplier report sharing
                    QWeb purchase report export
                    Odoo purchase report module
                    Report bundling wizard Odoo
                    pyminizip password ZIP
                    ir.actions.report QWeb PDF
                    ZIP file export wizard
                    Purchase document archiving
                    Odoo attachment ZIP export
                    PO PDF export Odoo
    """,
    'description': """ This feature allows users to export purchase order reports in bulk and securely download them as a password-protected ZIP file. By adding an additional layer of security, the exported ZIP file ensures that sensitive purchase order information remains protected. Users can generate multiple purchase order reports, compress them into a ZIP archive, and set a password before downloading. This functionality is ideal for maintaining confidentiality while sharing or storing reports.
                        Purchase order ZIP export
                        Export purchase reports Odoo
                        Purchase order report bundling
                        Password-protected ZIP Odoo
                        Secure PO report download
                        Batch purchase order export
                        Compressed purchase order reports
                        Export multiple purchase PDFs
                        Purchase report encryption
                        Download PO ZIP file Odoo
                        Encrypted ZIP purchase report
                        PO report password protection
                        Secure purchase document export
                        Odoo purchase report security
                        Protected ZIP file generation
                        Report compression with password
                        Secure supplier report sharing
                        QWeb purchase report export
                        Odoo purchase report module
                        Report bundling wizard Odoo
                        pyminizip password ZIP
                        ir.actions.report QWeb PDF
                        ZIP file export wizard
                        Purchase document archiving
                        Odoo attachment ZIP export
                        PO PDF export Odoo
    """,
    'category': 'tool',
    'license': 'OPL-1',
    'depends': ['purchase'],
    'data': [
        'security/ir.model.access.csv',
        'security/res_groups_view.xml',
        'views/purchase_order.xml',
        'wizard/export_purchase_pdf_wizard.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 15.00,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': True,
}

