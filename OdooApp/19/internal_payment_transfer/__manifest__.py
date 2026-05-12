# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Internal Payment Transfer',
    "author": "TechUltra Solutions Private Limited",
    "company": "TechUltra Solutions Private Limited",
    "website": "https://www.techultrasolution.com",
    'category': 'account',
    'version': '19.0.0.0',
    'summary': (
        'Transfer funds between internal bank and cash journals with paired '
        'payments, reconciliation, and clear transfer labels.'
    ),
    'description': """
Internal Payment Transfer lets you move liquidity between your own bank and cash
journals while keeping accounting entries aligned: a matching payment is created
on the destination journal and lines are reconciled using the company transfer
account configuration.
    """,
    'depends': ['account'],
    'data': [
        'views/account_payment_view.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 12.96,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    "license": "OPL-1",
}
