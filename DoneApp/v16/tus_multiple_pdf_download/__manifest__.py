# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': 'Bulk QWeb PDF Download | Password Protected ZIP Export | Multi-Document Report Manager',
    'version': '16.0.0.0',
    'author': "TechUltra Solutions Private Limited",
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'summary': """
    Easily export and download multiple QWeb reports in a single, password-protected ZIP file. Save time by compiling key business documents—such as Invoices, Sales Orders, Deliveries, Purchase Orders, and Manufacturing Orders—into one secure, compressed file.
    QWeb report export
    Odoo report ZIP export
    Export multiple QWeb reports
    Password protected ZIP reports
    Bulk QWeb report download
    Odoo document export tool
    Export Odoo invoices, sales, and deliveries
    Secure ZIP file for Odoo reports
    Download QWeb documents in bulk
    Odoo PDF report exporter with password protection
    Compress QWeb reports into ZIP file
    Export sales and invoice reports from Odoo
    Odoo batch export
    PDF report archiving Odoo
    Odoo automated report export
    Export manufacturing orders Odoo
    Sales and invoice document exporter
    Odoo QWeb PDF downloader
    """,
    'description': """ 
    Whether you're looking to compile documents like invoices (customer invoices, vendor bills, customer credit notes, vendor credit notes, payments), sales orders (including orders and quotations), deliveries (incoming and outgoing), purchase orders, or manufacturing orders (work orders and production orders), this functionality simplifies the process. It efficiently collects all the QWeb-generated documents you need into one convenient compressed file for easy access and storage.
    QWeb report export
    Odoo report ZIP export
    Export multiple QWeb reports
    Password protected ZIP reports
    Bulk QWeb report download
    Odoo document export tool
    Export Odoo invoices, sales, and deliveries
    Secure ZIP file for Odoo reports
    Download QWeb documents in bulk
    Odoo PDF report exporter with password protection
    Compress QWeb reports into ZIP file
    Export sales and invoice reports from Odoo
    Odoo batch export
    PDF report archiving Odoo
    Odoo automated report export
    Export manufacturing orders Odoo
    Sales and invoice document exporter
    Odoo QWeb PDF downloader
    """,
    'category': 'tool',
    'license': 'OPL-1',
    'depends': ['account', 'sale_management', 'purchase', 'stock', 'mrp'],
    'data': [
        'security/ir.model.access.csv',
        'security/res_groups_view.xml',
        'views/account_move.xml',
        'views/sale_order.xml',
        'views/mrp_production_order.xml',
        'views/stock_delivery.xml',
        'views/purchase_order.xml',
        'views/mrp_workorder.xml',
        'wizard/export_inv_wizard.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 30.00,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': True,
}
