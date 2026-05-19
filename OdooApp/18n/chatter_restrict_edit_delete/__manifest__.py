# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Restrict chatter Edit and Delete',
    'version': '18.0',
    'summary': """Restricts editing and deleting log notes in Odoo 18.
                    restrict chatter
                    disable chatter edit
                    disable chatter delete
                    chatter permissions
                    chatter security
                    mail.message security
                    mail.thread security
                    prevent message delete
                    prevent message edit
                    restrict edit and delete in odoo chatter
                    lock chatter messages for all users
                    allow only admins to delete chatter
                    prevent users from editing chatter notes
                    secure chatter for audits and compliance
                    odoo module to control chatter permissions
                    block delete of mail.message records
                    disable chatter message editing per group
    """,
    'description': """
        This module restricts the ability to edit and delete log notes (mail.message) in Odoo 18.
        It includes custom security rules and view modifications to enforce these restrictions.
        odoo chatter
        restrict chatter
        disable chatter edit
        disable chatter delete
        chatter permissions
        chatter security
        mail.message security
        mail.thread security
        prevent message delete
        prevent message edit
        restrict edit and delete in odoo chatter
        lock chatter messages for all users
        allow only admins to delete chatter
        prevent users from editing chatter notes
        secure chatter for audits and compliance
        odoo module to control chatter permissions
        block delete of mail.message records
        disable chatter message editing per group
    """,
    'author': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com',
    'category': 'Tools',
    'depends': ['mail'],
'assets': {
        'web.assets_backend': [
            'chatter_restrict_edit_delete/static/src/xml/chatter_views.xml',
            'chatter_restrict_edit_delete/static/src/core/common/message_inherit.js',
        ]
    },
    'data': [
        'security/chatter_restrict_edit_delete_group.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'installable': True,
    'price': 7,
    'currency': 'EUR',
    'auto_install': False,
    'license': 'OPL-1',
}