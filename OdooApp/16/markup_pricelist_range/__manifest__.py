# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Markup Pricelist Range',
    'version': '16.0.0.0',
    'summary': (
        'Cost-band pricelist rules: define minimum and maximum cost per rule and apply '
        'a markup percentage for cost-driven pricing on sales pricelists.'
    ),
    'description': """
Markup Pricelist Range extends pricelist rules with minimum and maximum cost boundaries
and markup-based unit prices when pricing is based on cost. Rules validate non-overlapping
cost ranges per pricelist and can refresh draft sales order line prices when markup changes.
    """,
    'author': 'TechUltra Solutions Private Limited',
    'license': 'OPL-1',
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com/',
    'depends': ['product', 'sale_management'],
    'data': [
        'views/cost_markup.xml',
        'views/product_template.xml',
    ],
    'images': [
        'static/description/main_screen.gif',
    ],
    'price': 18.00,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
}
