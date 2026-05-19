# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Restrict chatter Edit and Delete',
    'version': '16.0',
    'summary': 'Restricts editing and deleting log notes in Odoo 16.',
    'description': """
        This module restricts the ability to edit and delete log notes (mail.message) in Odoo 16.
        It includes custom security rules and view modifications to enforce these restrictions.
    """,
    'author': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com',
    'category': 'Tools',
    'depends': ['mail'],  # Depends on the 'mail' module for log notes (mail.message)
    'assets': {
        'mail.assets_messaging': [
            'chatter_restrict_edit_delete/static/src/models/message_action_list_inherit.js',
        ],

    },
    'data': [
        "security/chatter_restrict_edit_delete.xml",
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
}
