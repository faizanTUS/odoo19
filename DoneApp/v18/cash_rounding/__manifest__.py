# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': "POS Multiple Cash Rounding Methods | Payment Screen Rounding | Point of Sale Cash Management",
    'summary': """
                POS multiple cash rounding option on paymentscreen
                POS cash rounding
                Payment rounding
                Cash transaction adjustment
                Round-off amount
                Currency rounding
                Rounding method
                Cash payment precision
                Change calculation
                POS cash rounding strategy
                Apply cash rounding in POS
                POS payment screen customization
                Multiple rounding methods
                Rounding rule selection
                POS payment rounding options
                Dynamic rounding on payment
                Round to nearest 1 / 0.05 / 0.10
                Odoo POS rounding integration
                Rounding logic in POS session
                Multiple rounding options
                Rounding rule selector
                Custom rounding per transaction
                Round up/down logic
                Nearest rounding value
                Rounding difference account
                Manual override of rounding
                Per-currency rounding configuration
                Auto rounding on cash payments
                Rounding popup in POS
                """,
    'description': """
                Provided multiple option on the Payment screen for cash rounding.
                POS cash rounding
                Payment rounding
                Cash transaction adjustment
                Round-off amount
                Currency rounding
                Rounding method
                Cash payment precision
                Change calculation
                POS cash rounding strategy
                Apply cash rounding in POS
                POS payment screen customization
                Multiple rounding methods
                Rounding rule selection
                POS payment rounding options
                Dynamic rounding on payment
                Round to nearest 1 / 0.05 / 0.10
                Odoo POS rounding integration
                Rounding logic in POS session
                Multiple rounding options
                Rounding rule selector
                Custom rounding per transaction
                Round up/down logic
                Nearest rounding value
                Rounding difference account
                Manual override of rounding
                Per-currency rounding configuration
                Auto rounding on cash payments
                Rounding popup in POS
                
    """,
    'author': "TechUltra Solutions Private Limited",
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'category': "Point of Sale",
    'version': '18.0.0.0',
    'license': 'OPL-1',
    'depends': ['point_of_sale'],
    'assets': {
        'point_of_sale._assets_pos': [
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
