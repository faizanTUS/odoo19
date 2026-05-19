# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': 'Advanced POS Combo & Bundle Products',
    'version': '19.0.0.0',
    'category': 'Sales/Point of Sale',
    'author': 'Techultra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'summary': """Combo products with groups, list/grid view, max items and POS popup
    
    tus
    techultra
    techultra_private_limited_solution
    pos combo products
    pos bundle products
    advanced pos combos
    pos meal combo system
    pos product bundles
    combo products with groups
    pos combo popup selection
    pos bundle item validation
    configurable combo products
    point of sale combo module
    Advanced POS Combo & Bundle Products
    group products
    combo products with groups
    pos combo popup selection
    pos combo products
    pos product combo
    pos bundle products
    pos meal combo
    pos product bundles
    pos combo deals
    pos bundled items
    combo product configuration
    combo group management
    bundle product selection
    combo item popup
    combo product validation
    max item validation in pos
    combo quantity control
    dynamic combo pricing
    combo receipt display
    advanced pos combos
    pos combo popup selection
    list and grid product selection
    pos item grouping
    pos product grouping
    pos bundled product workflow
    customizable pos combos
    restaurant pos combo system
    cafe pos meal deals
    fast food pos combos
    retail pos bundle products
    supermarket pos bundle offers
    food ordering pos combos
    hospitality pos combo products
    restaurant pos combo system
    cafe pos meal deals
    fast food pos combos
    retail pos bundle products
    supermarket pos bundle offers
    food ordering pos combos
    hospitality pos combo products
    best pos combo module
    advanced combo product system
    pos bundle management
    combo product addon
    point of sale combo products
    pos product combo solution
    
    """,
    'description': """
Create advanced POS combo and bundle products with group-based selection, quantity limits, popup selection, and list or grid views. Perfect for meal deals, bundles, and retail offers.
==============================
* **Product Combo Configuration**: Is Combo Product, Max Combo Items, List/Grid display.
* **Combo Groups**: Reusable groups of products (min/max/default qty) assignable to combos.
* **Combo Line**: Direct component lines on product with min/max/default qty.
* **POS**: Select Combo Products popup (list or grid), quantity per item, max items validation.
* **POS Config**: Default Combo Display (list/grid).
* Keeps existing quantity per combo item and Combo Items tab for standard combos.


    tus
    techultra
    techultra_private_limited_solution
    pos combo products
    pos bundle products
    advanced pos combos
    pos meal combo system
    pos product bundles
    combo products with groups
    pos combo popup selection
    pos bundle item validation
    configurable combo products
    point of sale combo module
    Advanced POS Combo & Bundle Products
    group products
    combo products with groups
    pos combo popup selection
    pos combo products
    pos product combo
    pos bundle products
    pos meal combo
    pos product bundles
    pos combo deals
    pos bundled items
    combo product configuration
    combo group management
    bundle product selection
    combo item popup
    combo product validation
    max item validation in pos
    combo quantity control
    dynamic combo pricing
    combo receipt display
    advanced pos combos
    pos combo popup selection
    list and grid product selection
    pos item grouping
    pos product grouping
    pos bundled product workflow
    customizable pos combos
    restaurant pos combo system
    cafe pos meal deals
    fast food pos combos
    retail pos bundle products
    supermarket pos bundle offers
    food ordering pos combos
    hospitality pos combo products
    restaurant pos combo system
    cafe pos meal deals
    fast food pos combos
    retail pos bundle products
    supermarket pos bundle offers
    food ordering pos combos
    hospitality pos combo products
    best pos combo module
    advanced combo product system
    pos bundle management
    combo product addon
    point of sale combo products
    pos product combo solution
    
    """,
    'depends': ['product', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_combo_group_views.xml',
        'views/product_template_views.xml',
        'views/product_combo_views.xml',
        'views/pos_config_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_combo_advanced/static/src/css/pos_combo_advanced.css',
            'pos_combo_advanced/static/src/scss/combo_orderline.scss',
            'pos_combo_advanced/static/src/app/store/select_combo_products_popup/select_combo_products_popup.js',
            'pos_combo_advanced/static/src/app/store/select_combo_products_popup/select_combo_products_popup.xml',
            'pos_combo_advanced/static/src/app/store/pos_store_patch.js',
            'pos_combo_advanced/static/src/js/orderline_patch.js',

            # 'pos_combo_advanced/static/src/app/store/orderline_patch.js'
        ],
    },
    'images': ['static/description/main_screen.gif'],
    'price': 19.90,
    'currency': 'USD',
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}
