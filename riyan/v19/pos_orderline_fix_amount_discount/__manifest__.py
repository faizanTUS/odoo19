# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'POS OrderLine Fix Amount Discount',
    'version': '19.0.0.0',
    'author': 'TechUltra Solutions Private Limited',
    'category': 'Point of Sale',
    'website': 'https://www.techultrasolutions.com',
    "company": "TechUltra Solutions Private Limited",
    'summary': """
    The POS Order Line Fix Amount Discount module lets cashiers apply an exact dollar (or currency) discount to any single item in Odoo’s Point of Sale. Instead of typing 10 %, you type $5, $20, etc.; the line total updates instantly, the discount is recorded for reporting, and percentage discounts remain available. It installs in minutes, works on any POS device, and gives managers precise control over promotions, price-matching, or goodwill reductions.
    Odoo POS fixed discount
    POS line amount discount
    Odoo point of sale fixed amount off
    POS order line exact discount
    Odoo POS cash discount per item
    Fixed amount discount Odoo POS
    POS line discount module Odoo
    Odoo POS promotional discount amount
    POS fixed price reduction Odoo
    Odoo POS discount per product
    POS amount off Odoo
    Odoo POS line item discount
    Fixed discount Odoo app
    Odoo POS discount amount feature
    POS precise discount Odoo
    Odoo POS discount control
    Odoo POS discount functionality
    Odoo POS discount plugin
    POS discount amount extension
    Odoo POS discount customization
    Odoo POS fixed promo discount
    POS discount amount integration
    Odoo POS discount configuration
    Odoo POS discount management
    Odoo POS promotional amount off
    Odoo POS discount per line item
    Odoo POS fixed discount button
    Odoo POS discount amount button
    Odoo POS discount amount application
    Odoo POS discount amount reporting
    Odoo19
    Odoo18
    Odoo17
    TUS
    tus
    techultra solutions
    techultra
    techultra solutions private limited
    """,
    'description': """
        The POS Order Line Fix Amount Discount module for Odoo adds the functionality to apply a fixed amount discount directly to individual order lines in the Point of Sale (POS) system. This feature is essential for businesses that need to offer precise discount amounts rather than percentage-based discounts, providing flexibility and control over promotional activities.
        Odoo POS fixed discount
    POS line amount discount
    Odoo point of sale fixed amount off
    POS order line exact discount
    Odoo POS cash discount per item
    Fixed amount discount Odoo POS
    POS line discount module Odoo
    Odoo POS promotional discount amount
    POS fixed price reduction Odoo
    Odoo POS discount per product
    POS amount off Odoo
    Odoo POS line item discount
    Fixed discount Odoo app
    Odoo POS discount amount feature
    POS precise discount Odoo
    Odoo POS discount control
    Odoo POS discount functionality
    Odoo POS discount plugin
    POS discount amount extension
    Odoo POS discount customization
    Odoo POS fixed promo discount
    POS discount amount integration
    Odoo POS discount configuration
    Odoo POS discount management
    Odoo POS promotional amount off
    Odoo POS discount per line item
    Odoo POS fixed discount button
    Odoo POS discount amount button
    Odoo POS discount amount application
    Odoo POS discount amount reporting
    Odoo19
    Odoo18
    Odoo17
    TUS
    tus
    techultra solutions
    techultra
    techultra solutions private limited
    """,
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_order_view.xml',
        'views/res_config_settings.xml',
    ],
    'assets': {
        'point_of_sale.assets_prod': [
            'pos_orderline_fix_amount_discount/static/src/overrides/main.js',
            'pos_orderline_fix_amount_discount/static/src/control_buttons/fix_discount_btn.xml',
            'pos_orderline_fix_amount_discount/static/src/overrides/OrderLine.xml',
            'pos_orderline_fix_amount_discount/static/src/overrides/ticket_screen.js',
            'pos_orderline_fix_amount_discount/static/src/control_buttons/fix_discount_btn.js',
        ],
    },
    'images': [
        'static/description/main_screen.gif',
    ],
    'price': 19.97,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
}
