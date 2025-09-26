# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Enhanced Sale Price History',
    'version': '19.0',
    'author': 'TechUltra Solutions Private Limited',
    'category': 'Sales',
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com/',
    'summary': """
        Enhanced Sale Price History with filtering and limits
        OdooModule
        OdooCustomization
        OdooApps
        OdooDevelopment
        Sales Price History
        Product Price History
        Sale Order Tracking
        Quotation History
        Confirmed Order Price
        Draft Order Prices
        Product Template Extension
        Sales Reporting
        Historical Pricing
        Odoo Sales Module
        Custom Sale Price Log
        User Price Audit
        Track Product Pricing
        Odoo Product Enhancement
        Sales Order States
        Price Change Log
        Sales Price Analytics
        Configurable History Limit
        Pricelist Tracking
        Order State Filters
        Odoo Custom Module
        Sale Order Price Log
        Sales Order Enhancement
        Product Price Monitoring
        Dynamic Sales History
        Sales Analysis
        Order Line History
        Sale Price Audit Trail
        Sales Order Workflow
        Sales Data Tracking
        Odoo ERP Sales Tracking
        Real-time Price Logging
        Price Change History
        Odoo16
        Odoo17
        Odoo18
        TUS
        tus
        techultra solutions
        techultra
        techultra solutions private limited
        """,
    'description': """
        This module adds a "Sales Price History" tab to the product form, showing past sale prices based on order state filters (Draft, Quotation Sent, Confirmed). Users can configure which states to track and how many records to display from the settings.
        OdooModule
        OdooCustomization
        OdooApps
        OdooDevelopment
        Sales Price History
        Product Price History
        Sale Order Tracking
        Quotation History
        Confirmed Order Price
        Draft Order Prices
        Product Template Extension
        Sales Reporting
        Historical Pricing
        Odoo Sales Module
        Custom Sale Price Log
        User Price Audit
        Track Product Pricing
        Odoo Product Enhancement
        Sales Order States
        Price Change Log
        Sales Price Analytics
        Configurable History Limit
        Pricelist Tracking
        Order State Filters
        Odoo Custom Module
        Sale Order Price Log
        Sales Order Enhancement
        Product Price Monitoring
        Dynamic Sales History
        Sales Analysis
        Order Line History
        Sale Price Audit Trail
        Sales Order Workflow
        Sales Data Tracking
        Odoo ERP Sales Tracking
        Real-time Price Logging
        Price Change History
        Odoo18
        TUS
        tus
        techultra solutions
        techultra
        techultra solutions private limited
        """,
    "license": "OPL-1",
    'depends': ['sale_management', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_price_history_view.xml',
        'views/res_config_settings_view.xml',
        'data/data.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'installable': True,
    'application': False,
}
