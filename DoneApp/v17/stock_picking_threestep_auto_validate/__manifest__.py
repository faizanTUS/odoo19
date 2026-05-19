# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': "Stock Picking 3 Step Auto Validate",
    'author': 'TechUltra Solutions Private Limited',
    'category': 'sale/inventory',
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com',
    'version': '17.0.0.0',
    'summary': """
        Automate chained validation in Pick / Pack / Ship flows. 
        Optional auto validate on pack and delivery operation types.
        Odoo stock picking auto validate
        Odoo auto validate stock picking
        Odoo pick pack ship auto validate
        Odoo 3 step delivery auto validate
        Odoo automatic stock transfer validation
        Odoo delivery order auto validate
        Odoo warehouse auto validation
        Odoo inventory auto validate
        Odoo stock transfer automation
        Odoo warehouse automation
        Odoo picking type auto validation
        Odoo inventory workflow automation
        Odoo auto validate delivery order
        Odoo pick pack ship automation
        Odoo 3 step warehouse delivery
        Odoo automated picking validation
        Odoo validate stock picking automatically
        Odoo automatic delivery workflow
        How to auto validate stock picking in Odoo
        Automatically validate Pick Pack Ship transfers in Odoo
        Odoo module to auto validate delivery orders
        Odoo inventory module for automatic stock picking validation
        Auto validate 3 step delivery process in Odoo
        Odoo warehouse module for Pick Pack Ship automation
        Odoo auto validation for stock transfers by picking type
    """,
    'description': """
Automatically validate linked pickings after the pick transfer is validated,
for warehouses configured with a three-step outgoing route (Pick, Pack, Ship).

Features:
- Pack auto validate and Delivery auto validate on Inventory / Configuration / Operation Types
- Flags appear only when the warehouse uses a three-step outgoing configuration
- Server-side checks ensure the operation type is set as Pack or Out on a warehouse

Depends on Sale and Stock.

        Odoo stock picking auto validate
        Odoo auto validate stock picking
        Odoo pick pack ship auto validate
        Odoo 3 step delivery auto validate
        Odoo automatic stock transfer validation
        Odoo delivery order auto validate
        Odoo warehouse auto validation
        Odoo inventory auto validate
        Odoo stock transfer automation
        Odoo warehouse automation
        Odoo picking type auto validation
        Odoo inventory workflow automation
        Odoo auto validate delivery order
        Odoo pick pack ship automation
        Odoo 3 step warehouse delivery
        Odoo automated picking validation
        Odoo validate stock picking automatically
        Odoo automatic delivery workflow
        How to auto validate stock picking in Odoo
        Automatically validate Pick Pack Ship transfers in Odoo
        Odoo module to auto validate delivery orders
        Odoo inventory module for automatic stock picking validation
        Auto validate 3 step delivery process in Odoo
        Odoo warehouse module for Pick Pack Ship automation
        Odoo auto validation for stock transfers by picking type
""",
    'license': 'OPL-1',
    'depends': ['sale', 'stock'],
    'data': [
        'views/stock_picking_inherit.xml',
        'views/stock_picking_type_inherit.xml',
    ],
    'images': ['static/description/main_screen.gif'],
    'price': 17.47,
    'currency': 'USD',
    'application': True,
    'installable': True,
    'auto_install': False,
}
