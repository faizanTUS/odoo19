# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Stock Transfer Backdate Manager | Inventory Backdating & Audit Trail',
    'version': '17.0.0.0',
    'category': 'Inventory',
    'summary': """
    Stock Transfer Backdate Manager enables authorized users to backdate completed stock transfers, pickings, and stock moves while maintaining a complete audit trail.
    inventory backdate
    stock backdate
    odoo inventory backdate
    stock transfer backdate
    backdate stock picking
    inventory date correction
    stock operation backdate
    inventory backdate audit
    stock backdate audit trail
    odoo stock backdating
    inventory audit trail
    stock transfer audit
    inventory date change tracking
    stock date history
    original date preservation
    stock backdate compliance
    inventory audit ready
    stock backdate history
    user accountability inventory
    inventory traceability
    mass stock backdate
    bulk stock backdate
    backdate done stock transfers
    odoo stock wizard
    stock picking date update
    stock move date update
    inventory control module
    inventory management extension
    odoo stock customization
    inventory correction tool
    controlled stock backdate
    inventory backdate permission
    stock backdate security
    restricted inventory backdate
    inventory governance
    stock operation control
    odoo inventory addon
    odoo stock module
    inventory history tracking
    stock transfer history
    warehouse audit trail
    supply chain audit
    inventory compliance module
    stock management audit
    odoo18
    odoo19
    odoo17
    odoo16
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'description': """
    Stock Transfer Backdate Manager enables organizations to securely backdate completed stock transfers, pickings, and stock moves while maintaining a complete audit trail. The module provides controlled access for authorized users to modify completion dates of inventory transactions without losing historical information.
    inventory backdate
    stock backdate
    odoo inventory backdate
    stock transfer backdate
    backdate stock picking
    inventory date correction
    stock operation backdate
    inventory backdate audit
    stock backdate audit trail
    odoo stock backdating
    inventory audit trail
    stock transfer audit
    inventory date change tracking
    stock date history
    original date preservation
    stock backdate compliance
    inventory audit ready
    stock backdate history
    user accountability inventory
    inventory traceability
    mass stock backdate
    bulk stock backdate
    backdate done stock transfers
    odoo stock wizard
    stock picking date update
    stock move date update
    inventory control module
    inventory management extension
    odoo stock customization
    inventory correction tool
    controlled stock backdate
    inventory backdate permission
    stock backdate security
    restricted inventory backdate
    inventory governance
    stock operation control
    odoo inventory addon
    odoo stock module
    inventory history tracking
    stock transfer history
    warehouse audit trail
    supply chain audit
    inventory compliance module
    stock management audit
    odoo18
    odoo19
    odoo17
    odoo16
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com/',
    'depends': ['stock','stock_account'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'wizards/stock_backdate_wizard_views.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 11.95,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    "application": False,
}
