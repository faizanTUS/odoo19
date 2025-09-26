# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': 'Sales Commission Dashboard',
    'version': '19.0',
    'category': 'Sales/Sales',
    'sequence': 15,
    'summary': 'Real-time sales commission and activity tracking dashboard with user filters.',
    'description': """
Sales Commission Dashboard for Odoo 16, 17, and 18
==================================================
This module provides a modern and dynamic dashboard to track:
- Pending Quotations
- Pending Deliveries
- Payment Due Invoices
- Inactive Customers
- Commission Summary (Only in Odoo 18)

Key Features:
-------------
-️ Filter by Salesperson  
-️ Real-time data views  
-️ Clean, responsive layout  
-️ Commission Target/Achievement view in Odoo 18  
-️ No configuration required  

Great for Sales Managers and Executives to take quick actions based on live data.
    
    TUS
    tus
    Techultra
    techultra
    techultra private limited solution
    Techultra Private Limited Solution
    dashboard
    sales
    commission
    reporting
    crm
    salesperson
    odoo 16
    odoo 17
    odoo 18
    quotation
    delivery
    invoice
    target
    Odoo Sales Dashboard
    Odoo Sales Commission
    Odoo 18 Commission Summary
    Salesperson Dashboard Odoo
    Odoo Dashboard by User
    Odoo Real-Time Sales KPIs
    Odoo Quotation Tracker
    Odoo Pending Deliveries Dashboard
    Odoo Invoicing Dashboard
    Odoo Inactive Customers Report
    Odoo 16 17 18 Sales App
    Sales Management Odoo App
    Commission Target Tracking Odoo
    Odoo Sales Follow-up Dashboard
    Odoo Filter by Salesperson
    Odoo Sales Report Dashboard
    Sales Executive Dashboard Odoo
    Sales Analytics Odoo Module
    Odoo CRM Sales Dashboard
    Dynamic Odoo Sales Dashboard
    
    
    """,
    'author': 'Techultra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'license': 'OPL-1',

    # Dependencies
    'depends': [
        'base',
        'sale',
        'sales_team', 'sale_commission',
    ],

    'data': [
        'views/sales_commission_dashboard_view.xml',
    ],

    "assets": {
        "web.assets_backend": [
            "sales_commission_dashboard/static/src/css/sales_commission_dashboard.css",
            "sales_commission_dashboard/static/src/xml/sales_commission_dashboard.xml",
            "sales_commission_dashboard/static/src/js/sales_commission_dashboard.js",
        ]
    },
    "images": [
        "static/description/main_screen.gif",
    ],

    # Application settings
    'application': False,
    'installable': True,
    'auto_install': False,

    # Module price (if selling on Odoo Apps Store)
    'price': 14.14,
    'currency': 'USD',

    # Version compatibility
    'odoo_version': '18.0',
}
