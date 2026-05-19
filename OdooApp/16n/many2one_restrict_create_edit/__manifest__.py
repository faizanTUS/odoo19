# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Advanced Many2one Restrictions',
    'version': '16.0.0.0',
    'category': 'Technical/Tools',
    'summary': """
    Granular control over Create, Edit, and Open operations on Many2one fields across Sales, Purchase, Inventory, Products, and Invoicing.
    Many2one field restriction
    Many2one create edit restriction
    Disable create on Many2one field
    Restrict create and edit on dropdown
    Disable quick create in dropdown
    Disable open record from Many2one
    Field-level restriction module
    UI-based access control
    Group-based field restriction
    Master data creation control
    Prevent accidental record creation
    Sales form field restriction
    Purchase form field restriction
    Product selection restriction
    Product variant selection control
    Inventory field restriction
    Invoice field restriction
    Accounting form restriction
    Partner selection restriction
    Customer vendor selection control
    Dropdown restriction module
    Create and edit popup restriction
    Many2one permission control
    Form view restriction
    Restrict dropdown create option
    Field behavior control
    Data governance control
    Role-based UI restriction
    No create edit option
    Clean master data control
    Advanced field restriction
    ERP field restriction
    Sales purchase inventory restriction
    Product master control
    Invoice data control
    UI restriction without access rules
    Group-driven field control
    Prevent duplicate records
    Dropdown access restriction
    Field access manager
    odoo18
    odoo17
    odoo16
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'description': """
    Control Many2one dropdowns with group-based rules that block create, edit and open actions per module, while fields remain visible and readable with only write actions restricted. Apply separate rules to Sales, Purchase, Inventory, Product and Invoice modules to prevent accidental master-data changes without touching access rights or workflows, ensuring clean data governance and seamless user experience.
    Many2one field restriction
    Many2one create edit restriction
    Disable create on Many2one field
    Restrict create and edit on dropdown
    Disable quick create in dropdown
    Disable open record from Many2one
    Field-level restriction module
    UI-based access control
    Group-based field restriction
    Master data creation control
    Prevent accidental record creation
    Sales form field restriction
    Purchase form field restriction
    Product selection restriction
    Product variant selection control
    Inventory field restriction
    Invoice field restriction
    Accounting form restriction
    Partner selection restriction
    Customer vendor selection control
    Dropdown restriction module
    Create and edit popup restriction
    Many2one permission control
    Form view restriction
    Restrict dropdown create option
    Field behavior control
    Data governance control
    Role-based UI restriction
    No create edit option
    Clean master data control
    Advanced field restriction
    ERP field restriction
    Sales purchase inventory restriction
    Product master control
    Invoice data control
    UI restriction without access rules
    Group-driven field control
    Prevent duplicate records
    Dropdown access restriction
    Field access manager
    odoo18
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
    'depends': ['sale_management', 'purchase', 'stock', 'account'],
    'data': [
        'security/restrict_m2o_group.xml',
        'views/purchase_order.xml',
        'views/sale_order.xml',
        'views/account_move.xml',
        'views/stock_picking.xml',
        'views/product_template.xml',
        'views/product_product.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 12.00,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    "application": False,
}
