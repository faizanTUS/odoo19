# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Journal Access Management for Odoo | Journal Restriction by User | Secure Accounting Journals for Odoo',
    'version': '19.0.0.0',
    'company': 'TechUltra Solutions Private Limited',
    'summary': """Journal Access Management for Odoo allows administrators to restrict accounting journal access for specific users. The module automatically hides unauthorized journals and prevents restricted users from creating or modifying accounting records outside their assigned journals, ensuring secure and controlled financial operations.
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
    Journal Access Management for Odoo is a powerful accounting security module that enables administrators to control accounting journal access on a per-user basis. Businesses can assign specific journals to individual users while automatically hiding unauthorized journals from their view, ensuring secure and organized accounting operations. The module also enforces journal-level restrictions during record creation, editing, and validation to prevent unauthorized accounting actions. This helps organizations improve financial security, maintain operational control, and efficiently manage multi-team or department-based accounting workflows within Odoo.
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
        "views/account_move_views.xml",
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
