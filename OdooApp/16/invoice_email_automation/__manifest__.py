# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Accounting Invoice Auto Email',
    'version': '16.0.0.0',
    'category': 'Accounting',
    'author': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com',
    'company': 'TechUltra Solutions Private Limited',
    'summary': (
        'Automatically email validated customer invoices (PDF) using the standard invoice email template. '
        'Per-contact opt-in prevents duplicate sends. '
        'Odoo invoice email automation; automatic invoice email on validation.'
    ),
    'description': """
Automatically email validated customer invoices (PDF) using the standard accounting invoice email template.
Enable the option on a contact; when their customer invoices are posted, the PDF is sent without extra clicks.
Tracks whether the automated send already ran to avoid duplicate transmissions.
""",
    'depends': ['account'],
    'data': [
        'views/res_partner_view.xml',
        'views/account_move_view.xml',
    ],
    'price': 12.90,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    'application': False,
}
