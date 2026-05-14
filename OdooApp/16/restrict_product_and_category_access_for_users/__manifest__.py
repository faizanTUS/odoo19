# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Restrict Product and Category Access for Users',
    'version': '16.0',
    'category': 'Sales',
    'summary': 'Restrict users to access only allowed products or categories',
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'depends': ['base', 'product'],
    'description': """
        The Restrict Product and Category Access for Users module for Odoo allows administrators to manage product
        visibility based on user permissions. Using the Allow Product and Allow Category options, admins can restrict
        access to specific products and categories, ensuring users only see what they are authorized to view.
    """,
    'data': [
        'security/product_restriction_rules.xml',
        'views/res_users_views.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    "currency": "USD",
    "price": 10,
    'installable': True,
    "auto_install": False,
    'application': False,
    'license': 'OPL-1',
}
