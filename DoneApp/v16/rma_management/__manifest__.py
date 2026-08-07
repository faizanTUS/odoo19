# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'RMA Management | Customer & Supplier Return Management',
    'version': '16.0.0.0',
    'category': 'Sales/Sales',
    'summary': """
    A powerful Odoo module for managing Customer and Supplier RMAs with full support for returns, replacements, refunds, and inventory operations in one centralized system.
    RMA Management
    Return Merchandise Authorization
    Odoo RMA
    Customer Return Management
    Supplier Return Management
    RMA Odoo Module
    Product Return System
    Customer returns in Odoo
    Supplier RMA management
    Odoo return merchandise authorization
    Manage product returns Odoo
    RMA refund and replacement
    Inventory return management
    Odoo returns workflow
    Supplier return processing
    Customer RMA process
    Return authorization system
    Product replacement management
    Odoo refund management
    Reverse logistics Odoo
    Return order management
    Warranty return handling
    Odoo inventory returns
    RMA tracking system
    Business return management
    Automated RMA workflow
    Vendor return management
    Sales return processing
    odoo rma module
    rma software odoo
    customer returns odoo
    supplier rma odoo
    """,
    'description': """
    RMA Management | Customer & Supplier Return Management is a comprehensive Odoo module designed to streamline the entire Return Merchandise Authorization (RMA) process. It provides a centralized platform to efficiently handle customer returns, supplier returns, product replacements, refunds, and related inventory movements. The module ensures complete traceability and control from the initial return request through to final resolution, helping businesses reduce processing time and improve customer satisfaction.
    RMA Management
    Return Merchandise Authorization
    Odoo RMA
    Customer Return Management
    Supplier Return Management
    RMA Odoo Module
    Product Return System
    Customer returns in Odoo
    Supplier RMA management
    Odoo return merchandise authorization
    Manage product returns Odoo
    RMA refund and replacement
    Inventory return management
    Odoo returns workflow
    Supplier return processing
    Customer RMA process
    Return authorization system
    Product replacement management
    Odoo refund management
    Reverse logistics Odoo
    Return order management
    Warranty return handling
    Odoo inventory returns
    RMA tracking system
    Business return management
    Automated RMA workflow
    Vendor return management
    Sales return processing
    odoo rma module
    rma software odoo
    customer returns odoo
    supplier rma odoo
    """,
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com/',
    'depends': ['sale_management','purchase','stock','account','website_sale','portal'],
    'data': [
        'security/rma_security.xml',
        'security/ir.model.access.csv',
        'data/rma_data.xml',
        'data/mail_template_data.xml',
        'views/rma_reason_views.xml',
        'views/rma_restock_fee_views.xml',
        'views/rma_product_type_views.xml',
        'views/rma_reject_wizard_views.xml',
        'views/customer_rma_views.xml',
        'views/supplier_rma_views.xml',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/portal_templates.xml',
        'views/rma_menus.xml',
        'report/rma_report.xml',
        'report/rma_report_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'rma_management/static/src/js/portal_rma.js',
            'rma_management/static/src/xml/portal_rma_templates.xml',
            'rma_management/static/src/css/portal_rma.css',
        ],
    },
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 34.95,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    "application": False,
}
