# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': 'Quick Chatter Notes',
    'version': '18.0.0.0',
    'category': 'Productivity',
    "author": "TechUltra Solutions Private Limited",
    "website": "https://www.techultrasolutions.com",
    "company": "TechUltra Solutions Private Limited",
    'summary': """
    Quick Chatter Note is a productivity module that improves communication within Odoo’s chatter system by allowing users to create and reuse predefined notes with a Title, Content, User Assignment, and Global visibility options.
    Odoo Quick Chatter Note
    Odoo productivity module
    Odoo chatter notes
    Predefined notes in Odoo
    Odoo chatter enhancement
    Odoo communication efficiency
    Odoo message templates
    Odoo global notes
    Odoo user-wise notes
    Odoo note popup feature
    Odoo chatter quick notes
    Odoo smart messaging
    Odoo chatter automation
    Odoo note access control
    Odoo chatter shortcut notes
    Odoo predefined message content
    Odoo user-specific chatter notes
    Odoo quick reply notes
    Odoo efficiency tools
    Odoo internal communication module
    odoo18
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'description': """
    Quick Chatter Note is a productivity module that enhances Odoo’s chatter by allowing users to create and reuse predefined notes with a Title, Content, User Assignment, and Global visibility. A dedicated Notes icon opens a popup listing notes by index number, enabling users to insert content instantly into the chatter and eliminate repetitive typing.
    Odoo Quick Chatter Note
    Odoo productivity module
    Odoo chatter notes
    Predefined notes in Odoo
    Odoo chatter enhancement
    Odoo communication efficiency
    Odoo message templates
    Odoo global notes
    Odoo user-wise notes
    Odoo note popup feature
    Odoo chatter quick notes
    Odoo smart messaging
    Odoo chatter automation
    Odoo note access control
    Odoo chatter shortcut notes
    Odoo predefined message content
    Odoo user-specific chatter notes
    Odoo quick reply notes
    Odoo efficiency tools
    Odoo internal communication module
    odoo18
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'license': 'OPL-1',
    'depends': ['mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/quick_note_views.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'quick_chatter_notes/static/src/js/quick_notes_button.js',
            'quick_chatter_notes/static/src/xml/mail_composer_quick_notes.xml',
        ],
    },
    "images": ["static/description/main_screen.gif"],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,
    'price': 12.00,
    'currency': 'USD',

}
