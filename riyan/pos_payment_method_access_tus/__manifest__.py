# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    "name": "POS Payment Methods Access",
    "version": "19.0.0.0",
    "summary": """
    In odoo any user can see payment methods which have rights of POS, using our app the user can only see the payment methods which are allocated to them.
                POS payment method restriction
                User-specific payment methods
                Restrict POS payments per user
                Odoo POS access control
                POS user-based payment access
                Limit payment methods in POS
                Payment method visibility control
                Role-based payment access Odoo
                POS payment rights management
                User-level payment configuration
                POS payment method security
                Custom POS payment rules
                Assigned POS payment methods
                Odoo POS permissions
                Secure POS configuration
                Filtered payment options in POS
                POS payment method filter
                Per-user payment method visibility
                POS cashier payment restrictions
                Payment method assignment Odoo
    """,
    "description": """ 
        POS payment method restriction
        User-specific payment methods
        Restrict POS payments per user
        Odoo POS access control
        POS user-based payment access
        Limit payment methods in POS
        Payment method visibility control
        Role-based payment access Odoo
        POS payment rights management
        User-level payment configuration
        POS payment method security
        Custom POS payment rules
        Assigned POS payment methods
        Odoo POS permissions
        Secure POS configuration
        Filtered payment options in POS
        POS payment method filter
        Per-user payment method visibility
        POS cashier payment restrictions
        Payment method assignment Odoo
    """,
    "category": "Point of Sale",
    "author": "TechUltra Solutions Private Limited",
    'company': 'TechUltra Solutions Private Limited',
    "website": "https://www.techultrasolutions.com",
    "depends": ["point_of_sale"],
    "data": [
        "views/pos_payment_method.xml",
    ],
    "images": ["static/description/main_screen.gif"],
    "price": 19,
    "currency": "USD",
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}
