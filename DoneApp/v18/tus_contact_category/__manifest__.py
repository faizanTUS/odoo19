# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Odoo Contact Category Management | Hierarchical Contact Classification for Contacts',
    'version': '18.0.0.0',
    'category': 'Contacts',
    'author': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com',
    "company": "TechUltra Solutions Private Limited",
    'summary': """
    This module adds a hierarchical Contact Category system to Odoo for better contact organization. It enforces data governance through protected default categories and prevents accidental deletion. Categories can be archived while preserving historical consistency.
    contact category odoo
    odoo contact categories
    hierarchical contact categories
    contact category management
    contact classification odoo
    structured contact categories
    contact category hierarchy
    advanced contact categories
    enterprise contact categories
    governed contact categories
    parent child contact categories
    contact category tree
    contact taxonomy odoo
    contact categorization system
    contact segmentation odoo
    contact category control
    contact data governance
    protected contact categories
    non deletable contact categories
    archive contact categories
    odoo contacts enhancement
    odoo contact module extension
    res partner category management
    odoo contact classification module
    odoo hierarchical data model
    odoo parent store categories
    odoo contact category tree view
    odoo contact category count
    odoo contact reporting
    odoo data integrity module
    customer classification odoo
    vendor categorization odoo
    business contact organization
    crm contact categorization
    contact management framework
    enterprise contact management
    contact governance framework
    scalable contact categories
    structured crm contacts
    master data management contacts
    odoo18
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'description': """
    This module introduces structured, parent–child Contact Categories in Odoo to support clear and scalable contact classification. Categories display full hierarchical names and prevent recursive structures to maintain data integrity. A protected default category ensures safe fallback usage, while category deletion is blocked to avoid data loss. Contact counts and chatter tracking provide visibility and auditability for category management.
    contact category odoo
    odoo contact categories
    hierarchical contact categories
    contact category management
    contact classification odoo
    structured contact categories
    contact category hierarchy
    advanced contact categories
    enterprise contact categories
    governed contact categories
    parent child contact categories
    contact category tree
    contact taxonomy odoo
    contact categorization system
    contact segmentation odoo
    contact category control
    contact data governance
    protected contact categories
    non deletable contact categories
    archive contact categories
    odoo contacts enhancement
    odoo contact module extension
    res partner category management
    odoo contact classification module
    odoo hierarchical data model
    odoo parent store categories
    odoo contact category tree view
    odoo contact category count
    odoo contact reporting
    odoo data integrity module
    customer classification odoo
    vendor categorization odoo
    business contact organization
    crm contact categorization
    contact management framework
    enterprise contact management
    contact governance framework
    scalable contact categories
    structured crm contacts
    master data management contacts
    odoo18
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'depends': ['contacts', 'mail'],
    'data': [
        'security/contact_category_groups.xml',
        'security/ir.model.access.csv',
        'data/contact_category_data.xml',
        'views/contact_category_views.xml',
        'views/res_partner.xml',
    ],
    'images': [
        'static/description/main_screen.gif',
    ],
    'price': 11.90,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    "application": False,
}
