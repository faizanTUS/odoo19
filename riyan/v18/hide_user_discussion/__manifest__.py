# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    "name": "User wise Discuss Access Control | Hide Chat, Messaging & Discuss App",
    "version": "18.0.0.0",
    "category": "Productivity/Discuss",
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    "summary": """Hide Discuss app, messaging systray, and chat pop-ups unless a user is explicitly allowed — cleaner UI and tighter communication privacy.
    
    
    tus
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited
    discuss
    chat
    message
    communication
    user
    live chat
    user access control
    discuss access restriction
    chat access control
    messaging restriction
    hide discuss app
    disable chat odoo
    restrict messaging users
    user wise permission control
    hide chat icon
    disable discuss module
    control internal communication
    employee chat restriction
    limit user communication
    odoo discuss control
    messaging access manager
    user role restriction
    restrict discuss per user
    disable notifications odoo
    hide messaging menu
    block chat popups
    productivity tools odoo
    reduce distractions odoo
    employee focus tool
    secure internal communication
    privacy control messaging
    user group restriction
    backend access control
    frontend ui restriction
    odoo security module
    restrict user features
    manage user permissions
    internal chat control
    hide discuss icon
    disable discuss for users
    communication control system
    odoo usability improvement
    user interface cleaner
    role based visibility
    system access management
    odoo customization tool
    control user interface elements
    enterprise communication control
    restrict discuss functionality
    manage user roles effectively
    odoo productivity module
    clean dashboard experience
    user based feature toggle
    restrict app visibility
    employee restriction module
    control chat notification
    hide discuss menu
    disable discuss notifications
    restrict employee chat usage
    odoo backend restriction
    per user settings control
    advanced user management
    improve workflow efficiency
    business process control
    odoo performance usability
    reduce system noise
    simplify user interface
    enterprise user control
    communication governance
    access rights management
    user restriction tool
    smart permission control
    odoo system optimization
    modular access control
    role based communication
    control discuss access
    hide odoo chat
    block internal messaging
    restrict discuss access
    enable disable chat per user
    user level configuration
    odoo ui customization
    clean user experience
    
    """,
    "description": """
User wise Discuss Access Control | Hide Chat, Messaging & Discuss App for Odoo 18
=========================================

**What it does**
----------------
By default, **internal users do not** see Odoo **Discuss**, the **messaging / chat icon** in the top bar, or **floating chat windows**. You grant access **per user** with one security group (or the **Enable discussion** toggle on the user form).

**Why use it**
--------------
* Reduce distractions for teams that do not need live chat or Discuss.
* Limit who can use messaging features for **privacy** and **compliance**.
* Avoid unsolicited chat pop-ups after HR or other apps are installed.

**Typical setup**
-----------------
#. Install this module (everyone stays restricted until you allow them).
#. Open **Settings → Users**, pick a user, enable **Enable discussion** (or assign the **Discuss & live chat** group under **Access Rights**).
#. The user refreshes the browser; Discuss, the systray messenger, and chat bubbles work again for that user only.

**SEO / keywords**
------------------
Odoo 18, disable discuss, hide discuss, turn off chat, messaging menu, systray, live chat, per user, security group, privacy, UI cleanup, internal users.

    tus
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited
    discuss
    chat
    message
    communication
    user
    live chat
    user access control
    discuss access restriction
    chat access control
    messaging restriction
    hide discuss app
    disable chat odoo
    restrict messaging users
    user wise permission control
    hide chat icon
    disable discuss module
    control internal communication
    employee chat restriction
    limit user communication
    odoo discuss control
    messaging access manager
    user role restriction
    restrict discuss per user
    disable notifications odoo
    hide messaging menu
    block chat popups
    productivity tools odoo
    reduce distractions odoo
    employee focus tool
    secure internal communication
    privacy control messaging
    user group restriction
    backend access control
    frontend ui restriction
    odoo security module
    restrict user features
    manage user permissions
    internal chat control
    hide discuss icon
    disable discuss for users
    communication control system
    odoo usability improvement
    user interface cleaner
    role based visibility
    system access management
    odoo customization tool
    control user interface elements
    enterprise communication control
    restrict discuss functionality
    manage user roles effectively
    odoo productivity module
    clean dashboard experience
    user based feature toggle
    restrict app visibility
    employee restriction module
    control chat notification
    hide discuss menu
    disable discuss notifications
    restrict employee chat usage
    odoo backend restriction
    per user settings control
    advanced user management
    improve workflow efficiency
    business process control
    odoo performance usability
    reduce system noise
    simplify user interface
    enterprise user control
    communication governance
    access rights management
    user restriction tool
    smart permission control
    odoo system optimization
    modular access control
    role based communication
    control discuss access
    hide odoo chat
    block internal messaging
    restrict discuss access
    enable disable chat per user
    user level configuration
    odoo ui customization
    clean user experience
    """,
    "depends": ["mail", "base_setup"],
    "data": [
        "security/discussion_security.xml",
        "views/res_users_views.xml",
        "views/mail_menu_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "hide_user_discussion/static/src/xml/chat_hub_discussion.xml",
            "hide_user_discussion/static/src/js/discussion_feature_boot.js",
        ],
    },
    'images': [
        'static/description/main_screen.gif'
    ],
    'price': 12.00,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
