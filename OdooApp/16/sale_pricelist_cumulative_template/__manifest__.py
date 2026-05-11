# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    "name": "Cumulative Pricelist by Product Template",
    "summary": (
        "Evaluate pricelist quantity breaks using combined quantities of all "
        "variants of the same product template on the order or cart."
    ),
    "description": """
Cumulative Pricelist by Product Template
=========================================

When this option is enabled on a pricelist, minimum-quantity rules use the
total quantity of all sales order lines that share the same product template
(all variants together). The resulting unit price still applies per variant
line, so pricing stays correct for each SKU.

Works on sales orders and, with the website_sale dependency, on the e-commerce cart.
    """,
    "version": "16.0.0.0",
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
