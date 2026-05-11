# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    "name": "Cumulative Pricelist by Product Template",
    "summary": "Apply quantity-based pricelist tiers using combined quantities "
    "across all variants of the same product template on sales orders and eCommerce carts.",
    "description": """
Cumulative pricelist by product template
=======================================

This module extends standard pricelists so that, when enabled on a pricelist,
**minimum quantity** rules are evaluated against the **total quantity** of all
order lines that share the same **product template** (all variants combined),
while still returning a unit price for each variant line.

Typical use cases:

* Volume breaks that should apply when customers mix sizes or colors of the same product.
* Fair tiered pricing for configurable products sold as multiple variants on one order.

Website carts use the same server-side logic so storefront behavior matches the sales app.
    """,
    "version": "19.0.0.0",
    "category": "Sales/Pricing",
    "author": "TechUltra Solutions Private Limited",
    "company": "TechUltra Solutions Private Limited",
    "website": "https://www.techultrasolutions.com",
    "depends": ["sale_management", "website_sale"],
    "data": [
        "views/product_pricelist_views.xml",
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    "currency": "USD",
    "price": 24.00,
    "license": "OPL-1",
    "installable": True,
    "application": True,
    "auto_install": False,
}
