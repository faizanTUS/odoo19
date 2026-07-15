# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Bulk POS Order Cancellation | POS Order, Invoice & Delivery Management',
    'version': '16.0.0.0',
    'category': 'Point of Sale/Sales',
    'author': "TechUltra Solutions Private Limited",
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'summary': """
    Manage POS orders efficiently with bulk cancellation, draft reset, and deletion options, including support for related invoice and delivery order management.
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
    Bulk POS Order Cancellation | POS Order, Invoice & Delivery Management extends Odoo's Point of Sale functionality by providing efficient tools for managing and canceling POS orders directly from the list view. The module enables users to perform bulk order operations, reducing manual effort and simplifying order correction processes.
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
    "license": "OPL-1",
    "application": False,
}
