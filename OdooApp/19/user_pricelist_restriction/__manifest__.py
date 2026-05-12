# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Custom Pricelist Access',
    'version': '19.0.0.0',
    'category': 'Sales',
    'summary': 'Restrict internal users to pricelists assigned on their user profile.',
    'description': """
Assign allowed product pricelists per user. Internal users only see and use those pricelists
where product pricelists apply (for example on sale orders), while administrators set the list on each user form.
""",
    'author': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com',
    'company': 'TechUltra Solutions Private Limited',
    'depends': ['product', 'sale_management'],
    'data': [
        'security/pricelist_restriction_rule.xml',
        'views/product_pricelist_view.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 11.78,
    'currency': 'EUR',
}
