# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    "name": "Cumulative Pricelist by Product Template",
    "summary": (
        "Quantity discount tiers use the combined quantity of all variants "
        "of the same product template on the order or eCommerce cart."
    ),
    "description": """
Cumulative Pricelist by Product Template
========================================

This module extends pricelists so that, when the option is enabled on a
pricelist, **minimum quantity** rules are evaluated using the **total quantity
across all variants** of the same product template on the sales order or
website cart.

Typical use: volume breaks apply fairly when customers mix sizes, colors, or
other attributes of the same product.
    """,
    "version": "17.0.0.1.0",
    "category": "Sales/Pricing",
    "author": "TechUltra Solutions Private Limited",
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
