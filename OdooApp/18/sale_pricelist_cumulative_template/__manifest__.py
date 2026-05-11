# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    "name": "Cumulative Pricelist by Product Template",
    "summary": "Quantity tiers on a pricelist use the sum of all variants of the same product "
    "template on the order or eCommerce cart.",
    "description": """
Cumulative Pricelist by Product Template extends standard pricelists so that
minimum-quantity rules can be evaluated against the combined quantity of every
variant that shares the same product template on the sales order or website
cart, instead of each variant in isolation.
    """,
    "version": "18.0.1.0.0",
    "category": "Sales/Pricing",
    "author": "TechUltra Solutions Private Limited",
    "company": "TechUltra Solutions Private Limited",
    "website": "https://www.techultrasolutions.com",
    "depends": ["sale_management", "website_sale"],
    "data": [
        "views/product_pricelist_views.xml",
    ],
    "currency": "USD",
    "price": 24.00,
    "license": "OPL-1",
    "installable": True,
    "application": True,
    "auto_install": False,
}
