# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': 'POS Product Price Display Control | With Or Without Tax Price',
    'version': '17.0.0.0',
    'category': 'Sales/Point of Sale',
    'summary': """Display product prices on POS cards with tax or without tax
    
    
        tus
        techultra
        techultra_private_limited_solution
        point of sale
        pos
        price
        product price
        product price display
        product price display with tax  
        product price display without tax  
        pos product price display
        pos pricelist price update
        pos dynamic pricing
        pos real time price update
        pos price correction
        pos accurate product pricing
        pos multi pricelist support
        pos price visibility improvement
        pos retail pricing solution
        pos product tile price fix
        pos frontend price display
        pos pricing enhancement
        pos cashier price accuracy
        pos product card price
        pos automatic pricelist update
        pos price synchronization
        pos pricing control system
        pos advanced pricing module
        pos retail price management
        pos price display configuration
        pos session price refresh
        pos smart pricing
        pos pricing consistency
        pos price update without reload
        pos tax inclusive price display
        pos tax exclusive price display
        pos price with tax included
        pos price without tax
        pos fiscal position price update
        pos customer pricelist pricing
        pos promotional pricing display
        pos discount price display pos
        pos wholesale pricing pos
        pos b2b pricing pos
        pricelist
        pos pricelist
        pos dynamic pricing
        pos price update
        pos multi pricelist
        pos pricing fix
        pos accurate pricing
        pos retail pricing
        pos product price
        pos price control
        pos real time price
        pos price synchronization
        pos cashier pricing
        pos price visibility
        pos product tile price
        pos frontend pricing
        pos pricing enhancement
        pos pricing management
        pos automatic pricelist update
        pos retail price solution
        pos tax inclusive price
        pos tax exclusive price
        pos fiscal position pricing
        pos discount price display
        pos promotional pricing
        pos price shown with tax included
        pos price shown without tax
        pos pricelist not updating in pos
        pos incorrect price in pos
        pos price mismatch fix
        pos multi currency price display pos
        pos customer specific pricelist price
        pos dynamic price refresh pos
        pos retail chain pricing control
        pos price update when switching pricelist
        pos real time product price pos
        pos pricing consistency solution
        enterprise pos pricing
        advanced pos pricing module
        professional pos pricing solution
        pos pricing compliance
        pos pricing transparency
        pos scalable pos pricing
        production ready pos module
        upgrade safe pos customization
        retail automation pos pricing
        multi store pricing pos
        retail pos pricing usa
        vat price display pos
        gst price display pos
        uk retail pos pricing
        india gst pos pricing
        europe vat pos pricing
        pos price with vat included
        pos gst inclusive pricing
        pos multi currency price display
        pos currency based pricing
        pos retail chain pricing pos
        pos store level price control
        pos accurate billing display
        pos checkout price accuracy
        pos point of sale pricing fix
        pos price mismatch solution
        pos pricing automation
        pos smart retail pos
        pos configurable price display
        pos enterprise pricing solution
        pos upgrade safe pricing module
        pos lightweight pricing module
        pos ui pricing improvement
        pos modern pos pricing
        pos owl pos customization
        pos frontend patch pricing
        pos reliable price display
        pos price recalculation pos
        pos real time retail pricing
        pos price validation display
        pos product grid price update
        pos instant price refresh
        pos billing error prevention
        pos customer trust pricing
        pos advanced pos interface
        pos retail optimization tool
        pos professional pricing module
        pos production ready pos module
        pos pricing stability
        pos accurate checkout pricing
        pos retail price transparency
        pos price compliance solution
        pos business pricing control
        pos scalable pricing solution
    """,
    'description': """
POS Product Price Display Control | With Or Without Tax Price

This module gives businesses complete control over how product prices appear in the
Point of Sale interface. You can choose to display prices with sales tax or without
sales tax, depending on your business needs or regional requirements.


        tus
        techultra
        techultra_private_limited_solution
        point of sale
        pos
        price
        product price
        product price display
        product price display with tax  
        product price display without tax  
        pos product price display
        pos pricelist price update
        pos dynamic pricing
        pos real time price update
        pos price correction
        pos accurate product pricing
        pos multi pricelist support
        pos price visibility improvement
        pos retail pricing solution
        pos product tile price fix
        pos frontend price display
        pos pricing enhancement
        pos cashier price accuracy
        pos product card price
        pos automatic pricelist update
        pos price synchronization
        pos pricing control system
        pos advanced pricing module
        pos retail price management
        pos price display configuration
        pos session price refresh
        pos smart pricing
        pos pricing consistency
        pos price update without reload
        pos tax inclusive price display
        pos tax exclusive price display
        pos price with tax included
        pos price without tax
        pos fiscal position price update
        pos customer pricelist pricing
        pos promotional pricing display
        pos discount price display pos
        pos wholesale pricing pos
        pos b2b pricing pos
        pos pricelist
        pos dynamic pricing
        pos price update
        pos multi pricelist
        pos pricing fix
        pos accurate pricing
        pos retail pricing
        pos product price
        pos price control
        pos real time price
        pos price synchronization
        pos cashier pricing
        pos price visibility
        pos product tile price
        pos frontend pricing
        pos pricing enhancement
        pos pricing management
        pos automatic pricelist update
        pos retail price solution
        pos tax inclusive price
        pos tax exclusive price
        pos fiscal position pricing
        pos discount price display
        pos promotional pricing
        pos price shown with tax included
        pos price shown without tax
        pos pricelist not updating in pos
        pos incorrect price in pos
        pos price mismatch fix
        pos multi currency price display pos
        pos customer specific pricelist price
        pos dynamic price refresh pos
        pos retail chain pricing control
        pos price update when switching pricelist
        pos real time product price pos
        pos pricing consistency solution
        enterprise pos pricing
        advanced pos pricing module
        professional pos pricing solution
        pos pricing compliance
        pos pricing transparency
        pos scalable pos pricing
        production ready pos module
        upgrade safe pos customization
        retail automation pos pricing
        multi store pricing pos
        retail pos pricing usa
        vat price display pos
        gst price display pos
        uk retail pos pricing
        india gst pos pricing
        europe vat pos pricing
        pos price with vat included
        pos gst inclusive pricing
        pos multi currency price display
        pos currency based pricing
        pos retail chain pricing pos
        pos store level price control
        pos accurate billing display
        pos checkout price accuracy
        pos point of sale pricing fix
        pos price mismatch solution
        pos pricing automation
        pos smart retail pos
        pos configurable price display
        pos enterprise pricing solution
        pos upgrade safe pricing module
        pos lightweight pricing module
        pos ui pricing improvement
        pos modern pos pricing
        pos owl pos customization
        pos frontend patch pricing
        pos reliable price display
        pos price recalculation pos
        pos real time retail pricing
        pos price validation display
        pos product grid price update
        pos instant price refresh
        pos billing error prevention
        pos customer trust pricing
        pos advanced pos interface
        pos retail optimization tool
        pos professional pricing module
        pos production ready pos module
        pos pricing stability
        pos accurate checkout pricing
        pos retail price transparency
        pos price compliance solution
        pos business pricing control
        pos scalable pricing solution
    """,
    'depends': ['point_of_sale'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_product_price_display/static/src/js/products_widget_patch.js',
            'pos_product_price_display/static/src/xml/product_card.xml',
            'pos_product_price_display/static/src/xml/products_widget.xml',
        ],
    },
    "images": [
        "static/description/main_screen.gif",
    ],
    'currency': 'USD',
    'price': 12.00,
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}
