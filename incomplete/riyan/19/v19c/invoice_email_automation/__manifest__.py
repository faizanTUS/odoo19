# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Auto Send Customer Invoice Email | Automated Invoice Emailing After Validation',
    'version': '19.0.0.0',
    'category': 'Accounting',
    'author': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com',
    'company': 'TechUltra Solutions Private Limited',
    'summary': """
            Automatically email validated customer invoices (PDF) using the standard invoice email template.
            Per-contact opt-in prevents duplicate sends.
            Odoo invoice email automation; automatic invoice email on validation.

            Odoo auto send invoice email
            Odoo automatic invoice email
            Odoo invoice email automation
            Odoo send invoice after validation
            Odoo customer invoice email
            Odoo invoice email sender
            Odoo automated invoice delivery
            Odoo accounting automation
            Odoo invoice automation
            Odoo email invoice automatically
            Odoo customer invoice auto email
            Odoo send invoice by email automatically
            Odoo invoice validation email
            Odoo default invoice email template
            Odoo auto email invoice to customer
            Odoo backend invoice email automation
            Odoo no email composer invoice
            Odoo automatic billing email
            Odoo accounting invoice email
            Odoo invoice workflow automation
        """,
    'description': """
    Automatically email validated customer invoices (PDF) using the standard accounting invoice email template.
    Enable the option on a contact; when their customer invoices are posted, the PDF is sent without extra clicks.
    Tracks whether the automated send already ran to avoid duplicate transmissions.


    Odoo auto send invoice email
    Odoo automatic invoice email
    Odoo invoice email automation
    Odoo send invoice after validation
    Odoo customer invoice email
    Odoo invoice email sender
    Odoo automated invoice delivery
    Odoo accounting automation
    Odoo invoice automation
    Odoo email invoice automatically
    Odoo customer invoice auto email
    Odoo send invoice by email automatically
    Odoo invoice validation email
    Odoo default invoice email template
    Odoo auto email invoice to customer
    Odoo backend invoice email automation
    Odoo no email composer invoice
    Odoo automatic billing email
    Odoo accounting invoice email
    Odoo invoice workflow automation
    """,
    'depends': ['account'],
    'data': [
        'views/res_partner_view.xml',
        'views/account_move_view.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 12.90,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    'application': False,
}
