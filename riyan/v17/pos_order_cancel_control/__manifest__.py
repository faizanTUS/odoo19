# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Bulk POS Order Cancellation Tool',
    'version': '17.0.0.0',
    'category': 'Point of Sale/Sales',
    'summary': """
    Cancel Point of Sale orders directly from the list view with flexible options to reset to draft, permanently delete, and optionally cancel related delivery orders and invoices — all in one action.
    Odoo 18 POS order cancellation
    Cancel POS orders in Odoo
    POS order cancel module
    Bulk POS order cancellation
    Reset POS order to draft
    Delete POS order permanently
    POS order management addon
    Cancel POS delivery orders
    Cancel POS invoices
    POS stock picking cancellation
    POS invoice cancellation
    Mass POS order cancel
    POS order reset feature
    POS order delete option
    POS backend order management
    POS order correction tool
    POS order reversal system
    POS workflow enhancement
    Multi POS order action
    POS transaction cancellation
    POS order lifecycle control
    POS accounting reversal
    POS inventory reversal
    Cancel paid POS orders
    POS order administration tool
    POS cancel wizard
    POS list view action button
    Retail POS order cancellation
    POS order cleanup solution
    POS draft restore option
    POS bulk delete feature
    POS sales correction module
    POS order control management
    POS delivery and invoice cancel
    Advanced POS cancellation tool
    POS order edit after cancel
    POS transaction rollback
    POS stock and invoice reset
    POS manager cancellation feature
    Odoo POS bulk cancel orders
    Odoo POS reset to draft
    Odoo POS order delete
    Odoo POS delivery cancellation
    Odoo POS invoice cancel option
    Odoo POS order management tool
    odoo18
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'description': """
    POS Order Cancel is a utility module for Odoo that allows users to cancel POS orders directly from the list view. It supports cancelling and resetting orders to draft or permanently deleting them. Users can also optionally cancel related delivery orders and invoices in the same action. The module supports bulk operations and integrates smoothly with the standard Odoo Point of Sale workflow without requiring extra configuration.
    Odoo 18 POS order cancellation
    Cancel POS orders in Odoo
    POS order cancel module
    Bulk POS order cancellation
    Reset POS order to draft
    Delete POS order permanently
    POS order management addon
    Cancel POS delivery orders
    Cancel POS invoices
    POS stock picking cancellation
    POS invoice cancellation
    Mass POS order cancel
    POS order reset feature
    POS order delete option
    POS backend order management
    POS order correction tool
    POS order reversal system
    POS workflow enhancement
    Multi POS order action
    POS transaction cancellation
    POS order lifecycle control
    POS accounting reversal
    POS inventory reversal
    Cancel paid POS orders
    POS order administration tool
    POS cancel wizard
    POS list view action button
    Retail POS order cancellation
    POS order cleanup solution
    POS draft restore option
    POS bulk delete feature
    POS sales correction module
    POS order control management
    POS delivery and invoice cancel
    Advanced POS cancellation tool
    POS order edit after cancel
    POS transaction rollback
    POS stock and invoice reset
    POS manager cancellation feature
    Odoo POS bulk cancel orders
    Odoo POS reset to draft
    Odoo POS order delete
    Odoo POS delivery cancellation
    Odoo POS invoice cancel option
    Odoo POS order management tool
    odoo18
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'author': 'TechUltra Solutions Private Limited',
    "license": "OPL-1",
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com/',
    'depends': ['point_of_sale', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/pos_order_cancel_wizard_views.xml',
        'views/pos_order_views.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 15.90,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    "application": False,
}
