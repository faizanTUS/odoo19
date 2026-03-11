# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': 'Quick Pin for Chatter Messages | Pinned Messages in Chatter | Odoo Chatter Message Pin',
    'version': '17.0.0.0',
    'category': 'Discuss',
    'summary': """
    Pin important chatter messages across all Odoo documents for quick visibility.
    pin important messages
    message pin tool
    pinned messages feature
    message bookmark tool
    important notes pin
    message priority marker
    message spotlight tool
    quick message access
    message reference tool
    conversation message pin
    pinned notes manager
    message organizer tool
    important discussion highlight
    message navigation tool
    message visibility tool
    quick access to important messages
    important note marker
    message tracking tool
    message focus feature
    pin discussion messages
    highlight conversation notes
    important message manager
    chatter message pin
    chatter pinned messages
    chatter message highlight
    chatter important notes
    chatter message bookmark
    chatter message organizer
    chatter message navigation
    chatter discussion highlight
    odoo chatter message pin
    odoo pinned chatter messages
    odoo chatter message highlight
    odoo chatter notes pin
    odoo chatter message manager
    odoo chatter communication tool
    odoo chatter productivity feature
    odoo19
    odoo18
    odoo17
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'description': """
    This module enhances the Odoo chatter by allowing users to pin important messages or log notes for quick visibility,making it easier to find key information in long conversation threads. Users can pin or unpin messages with a single click. The module works with all models that use chatter (mail.thread) and uses the native pinned_at field for efficient message management.
    pin important messages
    message pin tool
    pinned messages feature
    message bookmark tool
    important notes pin
    message priority marker
    message spotlight tool
    quick message access
    message reference tool
    conversation message pin
    pinned notes manager
    message organizer tool
    important discussion highlight
    message navigation tool
    message visibility tool
    quick access to important messages
    important note marker
    message tracking tool
    message focus feature
    pin discussion messages
    highlight conversation notes
    important message manager
    chatter message pin
    chatter pinned messages
    chatter message highlight
    chatter important notes
    chatter message bookmark
    chatter message organizer
    chatter message navigation
    chatter discussion highlight
    odoo chatter message pin
    odoo pinned chatter messages
    odoo chatter message highlight
    odoo chatter notes pin
    odoo chatter message manager
    odoo chatter communication tool
    odoo chatter productivity feature
    odoo19
    odoo18
    odoo17
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'author': 'TechUltra Solutions Private Limited',
    "license": "OPL-1",
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com/',
    'depends': ['web', 'base', 'mail'],
    'data': [],
    "assets": {
        "web.assets_backend": [
            'tus_odoo_chatter_pin/static/src/css/style.css',
            'tus_odoo_chatter_pin/static/src/xml/pinnedMessages.xml',
            'tus_odoo_chatter_pin/static/src/js/pinMessage.js',
            'tus_odoo_chatter_pin/static/src/js/chatter.js',
        ],
    },
    "images": [
        "static/description/main_screen.gif",
    ],
    # 'price': 00.00,
    # 'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    "application": False,
}
