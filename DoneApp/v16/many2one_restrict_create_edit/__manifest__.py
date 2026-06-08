# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Advanced Many2one Restrictions | Disable Create, Edit & Open on Dropdowns',
    'version': '16.0.0.0',
    'category': 'Technical/Tools',
    'summary': """
        Master your data governance by selectively disabling 'Create', 'Create & Edit', and 'Open Record' actions on Many2one fields based on User Groups.

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
        tus
        TUS
        Techultra solutions
        Techultra solutions private solutions
        techultra solutions private limited
        """,
    'description': """
    Take full control over your ERP's master data integrity with the Advanced Many2one Restrictions module. 
    This powerful tool allows administrators to manage how users interact with Many2one dropdown fields without the need for complex security rule modifications. 

    By utilizing group-based permissions, you can dynamically restrict the ability to create new records, edit existing ones, or open related records directly from the UI. This ensures that only authorized personnel can add to your master data, preventing duplicates and spelling errors across Sales, Purchase, Inventory, and Invoicing modules.
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
