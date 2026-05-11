# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Payment Cashfree',
    'version': '19.0.0.0.1',
    'category': 'Accounting/Payment Providers',
    'summary': """
    Seamlessly integrate Cashfree with Odoo to enable secure, multi-mode online payments and automatic reconciliation.
    Cashfree Odoo integration.
    Odoo payment gateway
    Cashfree payment module
    Odoo online payments
    Secure payment integration Odoo
    TechUltra Cashfree integration
    Cashfree for Odoo
    Odoo UPI payments
    Odoo Net Banking integration
    Odoo wallet payments
    Cashfree hosted checkout
    Odoo eCommerce payments
    Cashfree reconciliation Odoo
    Seamless payment gateway Odoo
    Cashfree card payments
    Cashfree UPI gateway
    Odoo automated reconciliation
    Odoo payment processing
    Online payment solution Odoo
    Cashfree API integration Odoo
    Odoo financial automation
    Odoo Cashfree plugin
    Payment gateway for Odoo ERP
    Odoo customer payment experience
    Odoo secure checkout
    TechUltra payment integration
    Cashfree Odoo app
    Odoo credit card payments
    Cashfree Odoo setup
    Easy checkout Odoo
    Odoo Cashfree configuration
    Cashfree payment workflow Odoo
    Odoo seamless transaction
    Odoo hosted payment page
    Cashfree Odoo module download
    odoo18
    odoo19
    TUS
    Techultra
    Techultra Solutions Private Limited
    Techultra Solutions
    """,
    'description': """
    Cashfree is a popular payment gateway that offers a seamless and secure payment experience for Odoo customers. With TechUltra's integration, you can accept payments through Cards, UPI, Net Banking and Wallets. The module streamlines checkout, keeps users on a secure hosted page, and posts results back to your Odoo automatically for a smooth reconciliation.
    Cashfree Odoo integration.
    Odoo payment gateway
    Cashfree payment module
    Odoo online payments
    Secure payment integration Odoo
    TechUltra Cashfree integration
    Cashfree for Odoo
    Odoo UPI payments
    Odoo Net Banking integration
    Odoo wallet payments
    Cashfree hosted checkout
    Odoo eCommerce payments
    Cashfree reconciliation Odoo
    Seamless payment gateway Odoo
    Cashfree card payments
    Cashfree UPI gateway
    Odoo automated reconciliation
    Odoo payment processing
    Online payment solution Odoo
    Cashfree API integration Odoo
    Odoo financial automation
    Odoo Cashfree plugin
    Payment gateway for Odoo ERP
    Odoo customer payment experience
    Odoo secure checkout
    TechUltra payment integration
    Cashfree Odoo app
    Odoo credit card payments
    Cashfree Odoo setup
    Easy checkout Odoo
    Odoo Cashfree configuration
    Cashfree payment workflow Odoo
    Odoo seamless transaction
    Odoo hosted payment page
    Cashfree Odoo module download
    odoo18
    odoo19
    TUS
    Techultra
    Techultra Solutions Private Limited
    Techultra Solutions
    """,
    'author': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com/',
    'company': 'TechUltra Solutions Private Limited',
    'support': 'mailto:support@techultra.in',
    'depends': ['account_payment', 'payment'],
    'data': [
        "views/payment_cashfree_templates.xml",
        "views/payment_provider_form.xml",
        "data/payment_method_data.xml",
        "data/payment_provider_data.xml",
    ],
    'assets': {
        'web.assets_frontend': [
            'tus_payment_cashfree/static/src/interactions/payment_form.js',
        ],
    },
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 19.90,
    'currency': 'USD',
    'application': True,
    'installable': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'OPL-1',
}
