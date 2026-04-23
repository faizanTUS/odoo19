# -*- coding: utf-8 -*-
{
    "name": "Discuss & Chat Access Control — Per-User Privacy (Odoo 18)",
    "summary": "Hide Discuss app, messaging systray, and chat pop-ups unless a user is explicitly allowed — cleaner UI and tighter communication privacy.",
    "description": """
Discuss & Chat Access Control for Odoo 18
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
    """,
    "version": "18.0.1.0.0",
    "category": "Productivity/Discuss",
    "author": "Custom",
    "license": "LGPL-3",
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
    "installable": True,
    "application": False,
    "auto_install": False,
}
