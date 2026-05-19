# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Journal Restricted Users',
    'version': '17.0.0.0',
    'company': 'TechUltra Solutions Private Limited',
    'summary': """This module lets admins assign specific journals to each user and hides all others. It also blocks unauthorized journal use during creation or updates, ensuring secure and controlled accounting access.
    Odoo journal restriction
    Odoo restrict journals per user
    Odoo accounting security
    Odoo journal access control
    Odoo user-based journal access
    Odoo journal permissions
    Odoo allowed journals
    Odoo journal visibility
    Odoo accounting user roles
    Odoo restrict accounting journals
    Odoo journal access module
    Odoo financial control module
    Odoo accounting permissions
    Odoo multi-user accounting
    Odoo secure journal management
    Odoo accounting customization
    Odoo restrict user journals
    Odoo per-user journal rules
    Odoo access rules accounting
    Odoo journal rule enforcement
    Odoo accounting compliance
    Odoo journal security module
    Odoo advanced accounting control
    Odoo accounting audit control
    Odoo accounting workflow security
    Odoo journal visibility restriction
    Odoo user journal mapping
    Odoo manager journal assignment
    Odoo accounting authorization
    Odoo journal usage validation
    odoo18
    TUS
    tus
    techultra solutions
    techultra
    techultra solutions private limited
    """,
    'description': """
    This module restricts access to accounting journals on a per-user basis. Administrators can assign specific journals to each user, and the system automatically hides all other journals from their view. The module also enforces journal access on record creation and modification to prevent unauthorized actions, ensuring strong accounting security and operational control. Ideal for companies needing strict journal-level separation or multi-team accounting structures.
    Odoo journal restriction
    Odoo restrict journals per user
    Odoo accounting security
    Odoo journal access control
    Odoo user-based journal access
    Odoo journal permissions
    Odoo allowed journals
    Odoo journal visibility
    Odoo accounting user roles
    Odoo restrict accounting journals
    Odoo journal access module
    Odoo financial control module
    Odoo accounting permissions
    Odoo multi-user accounting
    Odoo secure journal management
    Odoo accounting customization
    Odoo restrict user journals
    Odoo per-user journal rules
    Odoo access rules accounting
    Odoo journal rule enforcement
    Odoo accounting compliance
    Odoo journal security module
    Odoo advanced accounting control
    Odoo accounting audit control
    Odoo accounting workflow security
    Odoo journal visibility restriction
    Odoo user journal mapping
    Odoo manager journal assignment
    Odoo accounting authorization
    Odoo journal usage validation
    odoo18
    TUS
    tus
    techultra solutions
    techultra
    techultra solutions private limited
    """,
    'category': 'Accounting',
    'author': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com',
    "depends": [
        "base",
        "account",
    ],
    "data": [
        "security/account_journal_restriction_security.xml",
        "data/account_journal_rule.xml",
        "views/res_users_view.xml",
        "views/account_journal_view.xml",
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    "price": 10,
    "currency": "USD",
    "application": False,
    "auto_install": False,
    "installable": True,
    "license": "OPL-1",
}
