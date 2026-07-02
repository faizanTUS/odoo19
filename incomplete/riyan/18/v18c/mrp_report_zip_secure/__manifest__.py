# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

# -*- coding: utf-8 -*-
{
    'name': 'Secure MRP Report ZIP Export | Password Protected Manufacturing Reports | Bulk PDF Download',
    'version': '18.0.0.0',
    'author': "TechUltra Solutions Private Limited",
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'summary': """ The Secure MRP Report ZIP Export | Password Protected Manufacturing Reports | Bulk PDF Download module streamlines the process of exporting and downloading Manufacturing Resource Planning (MRP) QWeb reports in a single, password-protected ZIP file. This feature ensures that all important documents, such as Manufacturing Orders, Work Orders, and Production Orders, are securely compiled and easily accessible
                        MRP report ZIP export
                        Odoo MRP document bundling
                        Manufacturing report compression
                        Secure MRP report archive
                        QWeb MRP export Odoo
                        Protected ZIP for MRP documents
                        Odoo manufacturing report packaging
                        Batch MRP report download
                        Password-protected manufacturing reports
                        Odoo MRP ZIP generation
                        MRP report encryption
                        Export BOM reports securely
                        Work order ZIP export
                        Odoo MRP file security
                        Centralized MRP report export
                        Manufacturing data ZIP archive
                        Odoo MRP report wizard
                        QWeb ZIP export for manufacturing
                        Compressed manufacturing reports Odoo
                        Encrypted MRP data download
    """ ,
    'description': """ The Secure MRP Report ZIP Export | Password Protected Manufacturing Reports | Bulk PDF Download module is designed to enhance the efficiency and security of managing MRP reports in Odoo. This functionality allows users to export multiple QWeb-generated reports into a single ZIP file that is both compressed for convenience and protected with a password for security. By centralizing all relevant MRP documents into one file, this module simplifies the process of report management, making it easier to store, share, and access important data.
                        MRP report ZIP export
                        Odoo MRP document bundling
                        Manufacturing report compression
                        Secure MRP report archive
                        QWeb MRP export Odoo
                        Protected ZIP for MRP documents
                        Odoo manufacturing report packaging
                        Batch MRP report download
                        Password-protected manufacturing reports
                        Odoo MRP ZIP generation
                        MRP report encryption
                        Export BOM reports securely
                        Work order ZIP export
                        Odoo MRP file security
                        Centralized MRP report export
                        Manufacturing data ZIP archive
                        Odoo MRP report wizard
                        QWeb ZIP export for manufacturing
                        Compressed manufacturing reports Odoo
                        Encrypted MRP data download
    """,
    'category': 'tool',
    'license': 'OPL-1',
    'depends': ['mrp'],
    'data': [
        'security/ir.model.access.csv',
        'security/res_groups_view.xml',
        'views/mrp_production_order.xml',
        'views/mrp_workorder.xml',
        'wizard/export_mrp_wizard.xml',
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
