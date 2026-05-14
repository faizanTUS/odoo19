# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': "Stock Picking 3 Step Auto Validate",
    'author': 'TechUltra Solutions Private Limited',
    'category': 'sale/inventory',
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com',
    'version': '18.0.0.0',
    'summary': (
        'Automate chained validation in Pick / Pack / Ship flows. '
        'Optional auto validate on pack and delivery operation types.'
    ),
    'description': """
Automatically validate linked pickings after the pick transfer is validated,
for warehouses configured with a three-step outgoing route (Pick, Pack, Ship).

Features:
- Pack auto validate and Delivery auto validate on Inventory / Configuration / Operation Types
- Flags appear only when the warehouse uses a three-step outgoing configuration
- Server-side checks ensure the operation type is set as Pack or Out on a warehouse

Depends on Sale and Stock.
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
