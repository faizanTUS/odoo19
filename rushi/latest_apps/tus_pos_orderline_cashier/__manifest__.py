# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    # App information
    'name': 'Odoo POS Orderline Cashier',
    'version': '19.0.0.0',
    'category': 'Point Of Sale',
    'author': 'TechUltra Solutions Private Limited',
    'license': 'OPL-1',
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com/',
    'summary': """The POS Multi-Cashier Selection app allows businesses to assign specific product categories to designated cashiers in the POS system. This ensures each cashier only handles their assigned items, streamlining operations, reducing errors, and improving customer service. Ideal for businesses like supermarkets, department stores, and specialty retailers, the app boosts productivity and simplifies cashier management.
    POS multi-cashier selection
    Odoo POS cashier assignment
    POS category-based cashier
    Odoo POS cashier control
    Multi-cashier POS system
    POS cashier by product category
    Assign cashiers to product categories
    Odoo POS retail management
    POS cashier restriction module
    Efficient cashier management in POS
    Odoo retail store POS customization
    Supermarket POS cashier ap
    """,
    'description': """
        In industries like supermarkets, electronics stores, and department chains, it's common for different cashiers to manage specific product categories. For instance, one cashier might handle clothing, another electronics, and another fresh produce. Managing these roles manually can be time-consuming and prone to errors.
        Our POS Multi-Cashier Selection app is built to simplify this process. With this module, you can easily assign specific product categories to designated cashiers in the POS system. This ensures that each cashier only handles their assigned products, reducing confusion and improving operational flow. Whether you're managing a multi-category retail outlet or a specialized store, this app enhances staff efficiency and customer satisfaction.
        POS multi-cashier selection
        Odoo POS cashier assignment
        POS category-based cashier
        Odoo POS cashier control
        Multi-cashier POS system
        POS cashier by product category
        Assign cashiers to product categories
        Odoo POS retail management
        POS cashier restriction module
        Efficient cashier management in POS
        Odoo retail store POS customization
        Supermarket POS cashier ap
    """,

    # Dependencies
    'depends': ['point_of_sale', 'pos_hr'],

    # Data
    'data': [
        'views/pos_config_views.xml',
        'views/pos_order_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'tus_pos_orderline_cashier/static/src/app/cashier_button/cashier.xml',
            'tus_pos_orderline_cashier/static/src/app/cashier_button/orderline.xml',
            'tus_pos_orderline_cashier/static/src/overrides/models/model.js',
            'tus_pos_orderline_cashier/static/src/overrides/orderrecipt.js',
            'tus_pos_orderline_cashier/static/src/app/cashier_button/cashier.js',
            'tus_pos_orderline_cashier/static/src/app/cashier_button/orderline.js',
            'tus_pos_orderline_cashier/static/src/app/cashier_button/pos_load_hr_employe.js',
        ],

    },

    # Images
    'images': [
        'static/description/main_screen.gif',
    ],

    # Technical
    'price': 13,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
}
