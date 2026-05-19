# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Website Sale Disable Out-of-Stock Variants',
    'version': '17.0.0.0',
    'category': 'Website/Website',
    'summary': """
    Disable out-of-stock product variants on the website and prevent customers from purchasing unavailable combinations.
    Website hide out of stock products
    Disable out of stock variants
    Product variant stock control
    Website stock visibility control
    Prevent purchase of out of stock variants
    eCommerce stock management
    Website sale stock restriction
    Variant availability manager
    Stock-based product visibility
    Website product availability control
    Out of stock product blocker
    Smart stock control for website
    Variant stock restriction
    Real-time stock visibility
    Website inventory visibility
    Add to cart stock restriction
    Website sale variant management
    Product stock dependent checkout
    Online shop stock control
    Website product stock filter
    Odoo website stock control
    Odoo website sale variant restriction
    Odoo eCommerce stock visibility
    Odoo product variant availability
    Odoo website prevent out of stock orders
    Odoo website inventory management
    Odoo 18 website stock module
    Odoo website sale customization
    Odoo variant stock automation
    Odoo shop stock availability
    Stock-based variant disabling
    Website stock protection module
    Variant stock availability control
    Dynamic stock-based product control
    Website sale product stock rule
    Odoo website product stock filter
    Odoo website add to cart restriction
    Out of stock variant manager
    Website stock management solution
    Odoo website stock visibility manager
    odoo18
    odoo17
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'description': """
    This module automatically disables out-of-stock product variants on the website to prevent customers from selecting unavailable combinations. Products remain visible in the shop, but variants with zero available quantity cannot be added to the cart. It improves the customer experience and helps avoid orders for unavailable stock. The feature can be easily enabled or disabled from the Website settings.
    Website hide out of stock products
    Disable out of stock variants
    Product variant stock control
    Website stock visibility control
    Prevent purchase of out of stock variants
    eCommerce stock management
    Website sale stock restriction
    Variant availability manager
    Stock-based product visibility
    Website product availability control
    Out of stock product blocker
    Smart stock control for website
    Variant stock restriction
    Real-time stock visibility
    Website inventory visibility
    Add to cart stock restriction
    Website sale variant management
    Product stock dependent checkout
    Online shop stock control
    Website product stock filter
    Odoo website stock control
    Odoo website sale variant restriction
    Odoo eCommerce stock visibility
    Odoo product variant availability
    Odoo website prevent out of stock orders
    Odoo website inventory management
    Odoo 18 website stock module
    Odoo website sale customization
    Odoo variant stock automation
    Odoo shop stock availability
    Stock-based variant disabling
    Website stock protection module
    Variant stock availability control
    Dynamic stock-based product control
    Website sale product stock rule
    Odoo website product stock filter
    Odoo website add to cart restriction
    Out of stock variant manager
    Website stock management solution
    Odoo website stock visibility manager
    odoo18
    odoo17
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'author': 'TechUltra Solutions Private Limited',
    "license": "OPL-1",
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com/',
    'depends': [
        'website_sale',
        'website_sale_stock',
    ],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 23.00,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    "application": False,
}
