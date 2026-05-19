# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Accounting Invoice Auto Email',
    'version': '18.0.0.0',
    'category': 'Accounting',
    'author': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com',
    "company": "TechUltra Solutions Private Limited",
    'summary': """
    Automatically generates and e-mails PDF invoices the moment they are validated.Removes manual steps, ensures prompt delivery, and prevents duplicate sends.
    Odoo automated invoice email
    Odoo invoice email automation
    Automatic invoice email on validation
    Odoo auto send invoice PDF
    Automated invoice delivery
    Odoo invoice auto email workflow
    Invoice email automation in Odoo
    Odoo customer invoice preference
    Customer-level invoice automation
    Odoo background invoice email sending
    Automatic invoice PDF emailing
    Odoo invoice email without manual action
    Automated invoice dispatch
    Odoo prevent duplicate invoice emails
    Invoice validation email automation
    Odoo accounting email automation
    Odoo default invoice email template
    Hands-free invoice emailing
    Automated invoicing communication
    Odoo finance workflow automation
    Automatic invoice PDF emailing
    Odoo invoice email without manual action
    Automated invoice dispatch
    Odoo prevent duplicate invoice emails
    Invoice validation email automation
    Odoo accounting email automation
    Odoo default invoice email template
    Hands-free invoice emailing
    Automated invoicing communication
    Odoo finance workflow automation
    odoo18
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'description': """
    Introduces a customer-level preference that, once activated, triggers fully-automated delivery of every validated invoice: the PDF is generated in the background and dispatched via the system’s default e-mail template without any additional user interaction, eliminating manual clicks, ensuring consistency, and preventing duplicate transmissions.
    Odoo automated invoice email
    Odoo invoice email automation
    Automatic invoice email on validation
    Odoo auto send invoice PDF
    Automated invoice delivery
    Odoo invoice auto email workflow
    Invoice email automation in Odoo
    Odoo customer invoice preference
    Customer-level invoice automation
    Odoo background invoice email sending
    Automatic invoice PDF emailing
    Odoo invoice email without manual action
    Automated invoice dispatch
    Odoo prevent duplicate invoice emails
    Invoice validation email automation
    Odoo accounting email automation
    Odoo default invoice email template
    Hands-free invoice emailing
    Automated invoicing communication
    Odoo finance workflow automation
    Automatic invoice PDF emailing
    Odoo invoice email without manual action
    Automated invoice dispatch
    Odoo prevent duplicate invoice emails
    Invoice validation email automation
    Odoo accounting email automation
    Odoo default invoice email template
    Hands-free invoice emailing
    Automated invoicing communication
    Odoo finance workflow automation
    odoo18
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/account_move_view.xml',
    ],
    'images': [
        'static/description/main_screen.gif',
    ],
    'price': 12.90,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    "application": False,
}
