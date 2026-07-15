# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Portal User Chat | Portal to Internal & Portal Messaging',
    'category': 'Services',
    'version': '17.0.0.0',
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'summary': """
    A powerful Odoo module that enables real-time messaging between portal users and internal teams, enhancing collaboration and communication within the Odoo portal.
    Odoo Portal Chat
    Portal User Chat Odoo
    Odoo Portal Messaging
    Portal to Internal Chat Odoo
    Odoo Customer Portal Chat
    Real-time chat for Odoo portal
    Odoo portal internal messaging
    Portal user to internal chat Odoo
    Customer portal messaging Odoo
    Odoo portal collaboration chat
    Live chat between portal and internal users Odoo
    Odoo portal user communication module
    Enable chat in Odoo customer portal
    Odoo vendor portal messaging
    Real-time messaging in Odoo portal
    Odoo portal extension chat
    Odoo customer engagement portal chat
    Portal to portal messaging Odoo
    Secure chat for Odoo portal users
    Odoo portal live chat module
    Internal and external chat Odoo
    Odoo partner portal communication
    Advanced portal chat system Odoo
    Odoo portal real-time messaging
    Chat system for Odoo portal users
    Odoo customer support portal chat
    Odoo portal collaboration tool
    Portal messaging extension Odoo
    Odoo portal user interaction module
    Integrated chat for Odoo portal
    """,
    'description': """
    This is an advanced Odoo module that extends the standard portal functionality by adding real-time chat capabilities. It allows portal users (customers, vendors, and partners) to communicate directly with internal team members as well as with other portal users within the same interface. This module transforms the Odoo portal into a collaborative platform, enabling seamless messaging, faster query resolution, and improved customer engagement while maintaining full security and ease of use.
    Odoo Portal Chat
    Portal User Chat Odoo
    Odoo Portal Messaging
    Portal to Internal Chat Odoo
    Odoo Customer Portal Chat
    Real-time chat for Odoo portal
    Odoo portal internal messaging
    Portal user to internal chat Odoo
    Customer portal messaging Odoo
    Odoo portal collaboration chat
    Live chat between portal and internal users Odoo
    Odoo portal user communication module
    Enable chat in Odoo customer portal
    Odoo vendor portal messaging
    Real-time messaging in Odoo portal
    Odoo portal extension chat
    Odoo customer engagement portal chat
    Portal to portal messaging Odoo
    Secure chat for Odoo portal users
    Odoo portal live chat module
    Internal and external chat Odoo
    Odoo partner portal communication
    Advanced portal chat system Odoo
    Odoo portal real-time messaging
    Chat system for Odoo portal users
    Odoo customer support portal chat
    Odoo portal collaboration tool
    Portal messaging extension Odoo
    Odoo portal user interaction module
    Integrated chat for Odoo portal
    """,
    'category': 'tool',
    'license': 'OPL-1',
    'depends': ['website', 'web', 'mail', 'portal', 'im_livechat'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/res_user.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'mail/static/src/core/public_web/**/*',
            'mail/static/src/discuss/core/public_web/**/*.js',
            'mail/static/src/discuss/core/public_web/**/*.xml',
            "im_livechat/static/src/core/public_web/**/*",
            'web/static/src/views/fields/file_handler.*',
            'web/static/src/views/fields/formatters.js',
            'web/static/src/webclient/navbar/navbar.xml',
            'web/static/src/webclient/navbar/navbar.js',
            'mail/static/src/model/**/*',
            'mail/static/src/core/common/**/*',
            'mail/static/src/core/common/store_service.js',
            'mail/static/src/discuss/call/common/**',
            'mail/static/src/discuss/typing/**/*',
            'mail/static/src/utils/common/**/*',
            'mail/static/src/discuss/call/common/**/*',
            'mail/static/src/discuss/typing/**/*',
            'mail/static/src/core/public_web/discuss_app_model.js',
            'mail/static/src/core/public_web/thread_model_patch.js',
            'mail/static/src/core/public_web/out_of_focus_service_patch.js',
            ('remove', 'mail/static/src/**/*.dark.scss'),
            'web/static/lib/odoo_ui_icons/style.css',
            'web/static/src/core/browser/title_service.js',
            'mail/static/src/core/web/messaging_menu_quick_search.js',
            'mail/static/src/core/web/messaging_menu_quick_search.xml',
            'mail/static/src/core/web/chat_window/**/*',
            'mail/static/src/core/web/chat_window/**/*',
            'mail/static/src/core/web/messaging_menu_patch.xml',
            'mail/static/src/discuss/core/web/discuss_core_web_service.js',
            'mail/static/src/discuss/core/web/messaging_menu_patch.js',
            'mail/static/src/discuss/core/web/messaging_menu_patch.xml',
            'mail/static/src/discuss/core/web/thread_model_patch.js',
            'mail/static/src/core/public_web/messaging_menu.js',
            'mail/static/src/core/public_web/messaging_menu.xml',
            'mail/static/src/core/public_web/messaging_menu.scss',
            'mail/static/src/core/public_web/notification_item.js',
            'mail/static/src/core/public_web/notification_item.scss',
            'mail/static/src/core/public_web/notification_item.xml',
            'mail/static/src/core/public_web/notification_item.dark.scss',
            'im_livechat/static/src/embed/common/chat_window_patch.js',
            'website_portal_chat/static/src/js/portal_service.js',
            'website_portal_chat/static/src/js/dropdow_fix.js',
            'website_portal_chat/static/src/js/messaging_menu_patch.js',
            'website_portal_chat/static/src/xml/messaging_menu_patch.xml',
            'website_portal_chat/static/src/css/style.css',
            'website_portal_chat/static/src/scss/new_style.scss',
        ],
    },
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 41.99,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'application': True,
}