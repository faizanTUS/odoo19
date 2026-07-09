# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': "POS Multiple Cash Rounding Methods | Payment Screen Rounding | Point of Sale Cash Management",
    'summary': "POS multiple cash rounding option on paymentscreen",
    'description': """
        Provided multiple option on the Payment screen for cash rounding.
    """,
    'author': "TechUltra Solutions Private Limited",
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'category': "Point of Sale",
    'version': '16.0.0.2',
    'license': 'OPL-1',
    'depends': ['point_of_sale'],
    'assets': {
        'point_of_sale.assets': [
            'cash_rounding/static/src/js/models.js',
            'cash_rounding/static/src/js/PaymentScreen.js',
            'cash_rounding/static/src/xml/pos_cash_rounding.xml',
        ],
    },
    'data': [],
    'images': ["static/description/main_screen.gif"],
    'application': False,
    'installable': True,
    'auto_install': False,
    'price': 15.00,
    'currency': 'EUR',
}
