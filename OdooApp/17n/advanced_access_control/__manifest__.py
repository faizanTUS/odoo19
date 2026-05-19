# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
{
    "name": "Advanced Access Control and UI Restrictions Manager | Hide Chatter, Developer Mode, Buttons, Menus and Actions",
    "version": "17.0.0.0",
    "category": "Administration/Access Rights",
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    "summary": """Odoo 17 advanced access rights: per-user model CRUD, field invisible/readonly/required with conditions,
     hide menus/buttons/tabs, export & duplicate control, global read-only, hide chatter, disable debug—centralized 
     policies with optional audit.
    
    
    
    tus
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited 
    access control
    user access management
    advanced access control
    role based access
    dynamic access rules
    user permission control
    data security management
    ui access control
    hide buttons
    hide menu
    hide tabs
    restrict export
    disable export
    block print
    disable print
    restrict import
    disable import
    prevent duplicate
    user restrictions
    action restrictions
    menu visibility control
    form view control
    list view restrictions
    backend security
    frontend security
    http security
    data protection system
    user level security
    access policy manager
    dynamic permissions
    granular access control
    record action control
    enterprise security
    business data security
    access rules engine
    security policy manager
    custom access rules
    advanced user roles
    system security tool
    access restriction module
    user control system
    workflow restriction
    operation control
    data leakage prevention
    secure user interface
    access governance
    ui restriction manager
    action control system
    user permission system
    smart access control
    secure business operations
    access management system
    restriction manager
    model access control
    user activity restriction
    advanced security tool
    policy based access
    access automation
    security enhancement
    user control dashboard
    access configuration tool
    access flexibility
    system control manager
    fine grained permissions
    user restriction engine
    secure workflow system
    data access limitation
    user action blocker
    enterprise access control
    custom security rules
    user interface control
    access logic manager
    permission customization
    data visibility control
    access restriction engine
    smart security system
         
     
     """,
    "description": """
Advanced Access Control & UI Restrictions Manager | Hide Chatter, Developer Mode, Buttons, Menus & Actions
=======================================

**Keywords (SEO / discovery):** Odoo 17 access rights manager, granular permissions, field-level
security, hide menu Odoo, hide button form view, read-only user, disable developer mode,
hide chatter, model access control, export restriction, duplicate restriction, UI access rules,
notebook tab hide, conditional field readonly, enterprise security, compliance, least privilege.

**What this module does**
-------------------------

Central **access policies** assign users or groups. Each policy can:

* **Global:** Force UI read-only on forms and lists, hide mail chatter, block developer/debug
  mode for the session, and optionally enforce create/write/unlink at the ORM level (with a safe
  whitelist for system chatter and this module’s own models).
* **Per model:** Allow or deny read, create, write, unlink, **export**, and **duplicate**, with an
  optional **record domain** so rules apply only to matching records (advanced).
* **Per field:** Set **invisible**, **readonly**, or **required**, with an optional **client
  expression** (e.g. ``state == 'done'``) so modifiers apply only when the expression is true.
* **Menus:** Hide specific menu entries (and their subtrees) from the navigation.
* **Buttons & tabs:** Hide form buttons by XML ``name`` and notebook pages by ``string``.
* **Audit (optional):** When enabled on a policy, denied operations (from this module’s rules) are
  logged for review.

 
   
    tus
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited
    access control
    user access management
    advanced access control
    role based access
    dynamic access rules
    user permission control
    data security management
    ui access control
    hide buttons
    hide menu
    hide tabs
    restrict export
    disable export
    block print
    disable print
    restrict import
    disable import
    prevent duplicate
    user restrictions
    action restrictions
    menu visibility control
    form view control
    list view restrictions
    backend security
    frontend security
    http security
    data protection system
    user level security
    access policy manager
    dynamic permissions
    granular access control
    record action control
    enterprise security
    business data security
    access rules engine
    security policy manager
    custom access rules
    advanced user roles
    system security tool
    access restriction module
    user control system
    workflow restriction
    operation control
    data leakage prevention
    secure user interface
    access governance
    ui restriction manager
    action control system
    user permission system
    smart access control
    secure business operations
    access management system
    restriction manager
    model access control
    user activity restriction
    advanced security tool
    policy based access
    access automation
    security enhancement
    user control dashboard
    access configuration tool
    access flexibility
    system control manager
    fine grained permissions
    user restriction engine
    secure workflow system
    data access limitation
    user action blocker
    enterprise access control
    custom security rules
    user interface control
    access logic manager
    permission customization
    data visibility control
    access restriction engine
    smart security system

    """,
    "depends": ["base", "web", "mail", "base_import"],
    "data": [
        "security/advanced_access_groups.xml",
        "security/ir.model.access.csv",
        "views/advanced_access_policy_views.xml",
        "views/advanced_access_audit_views.xml",
        "views/menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "advanced_access_control/static/src/js/aac_session_utils.js",
            "advanced_access_control/static/src/js/form_controller_patch.js",
            "advanced_access_control/static/src/js/form_controller_duplicate_patch.js",
            "advanced_access_control/static/src/js/form_renderer_mail_patch.js",
            "advanced_access_control/static/src/js/list_controller_export_patch.js",
            "advanced_access_control/static/src/js/aac_action_menus_print_patch.js",
            "advanced_access_control/static/src/js/aac_import_records_patch.js",
        ],
    },
    'images': [
        'static/description/main_screen.gif'
    ],
    'price': 45.00,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    "post_init_hook": "post_init_hook",
}
