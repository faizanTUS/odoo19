# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': 'Advanced Form Warnings | Dynamic Alert Rules | Smart Record Alerts',
    'version': '17.0.0.0',
    'category': 'Productivity',
    'summary': """
    Display dynamic conditional alerts on any Odoo form view based on rules, domains, user groups, and other criteria.
    dynamic warnings
    conditional alerts
    form warning messages
    dynamic alert rules
    rule based alerts
    smart form alerts
    conditional warning rules
    dynamic alert manager
    advanced form warnings
    rule based notifications
    form alert system
    smart warning engine
    dynamic notification rules
    custom alert manager
    flexible alert rules
    intelligent alert system
    form warning rules
    conditional notification alerts
    dynamic message alerts
    smart conditional warnings
    automated alert rules
    dynamic warning manager
    configurable alert rules
    advanced alert manager
    rule driven alerts
    smart notification alerts
    custom warning alerts
    conditional message system
    dynamic rule alerts
    form alert notifications
    odoo dynamic warnings
    odoo form alerts
    odoo conditional warnings
    odoo custom alerts
    odoo warning rules
    dynamic warnings for odoo forms
    conditional alerts for odoo
    smart alerts for odoo forms
    advanced alerts for odoo
    dynamic alert rules for odoo
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'description': """
    Dynamic Warnings allows you to create custom alerts that appear on any form view in Odoo such as Contacts, Sales Orders, Products, or Invoices. Alerts are triggered based on configurable domain conditions and can be styled as Info, Warning, or Danger messages. You can restrict alerts by user groups, validity dates, or company to control exactly when and to whom the warning is shown.
    dynamic warnings
    conditional alerts
    form warning messages
    dynamic alert rules
    rule based alerts
    smart form alerts
    conditional warning rules
    dynamic alert manager
    advanced form warnings
    rule based notifications
    form alert system
    smart warning engine
    dynamic notification rules
    custom alert manager
    flexible alert rules
    intelligent alert system
    form warning rules
    conditional notification alerts
    dynamic message alerts
    smart conditional warnings
    automated alert rules
    dynamic warning manager
    configurable alert rules
    advanced alert manager
    rule driven alerts
    smart notification alerts
    custom warning alerts
    conditional message system
    dynamic rule alerts
    form alert notifications
    odoo dynamic warnings
    odoo form alerts
    odoo conditional warnings
    odoo custom alerts
    odoo warning rules
    dynamic warnings for odoo forms
    conditional alerts for odoo
    smart alerts for odoo forms
    advanced alerts for odoo
    dynamic alert rules for odoo
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
    'depends': ['web', 'base'],
    'data': [
        'security/dynamic_warning_security.xml',
        'security/ir.model.access.csv',
        'views/dynamic_warning_rule_views.xml',
        'views/dynamic_warning_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dynamic_warnings/static/src/form_controller_patch.js',
        ],
    },
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 22.90,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    "application": False,
}
