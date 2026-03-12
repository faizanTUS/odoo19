# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    "name": "Cumulative Pricelist by Product Template",
    "summary": """Apply quantity discount tiers cumulatively across variants of the same product template
    cumulative pricelist by product template
    cumulative quantity discounts
    product variant quantity discount
    dynamic pricing by product template
    Odoo cumulative pricelist module
    quantity-based tiered pricing Odoo
    product template discount aggregation
    multi-variant cumulative pricing
    Odoo pricelist quantity discount
    cumulative pricing for product variants
    cumulative discount pricing Odoo
    tiered pricing across product variants
    quantity discount automation Odoo
    apply discounts by product template
    multi-variant discount pricing strategy
    Odoo sales pricelist customization
    volume pricing for product variants
    aggregate variant quantities for discount
    Odoo product pricing optimization
    advanced pricelist rules Odoo
    cumulative quantity discount management
    price breaks for product templates
    discount tiers based on combined quantity
    flexible pricelist discounts Odoo
    Odoo sales order pricing rules
    cumulative pricing rules for variants
    discount pricing across product variants
    Odoo pricing module for product templates
    automated tiered discounts Odoo
    product bundle pricing by template
    cumulative price breaks in sales orders
    managing discounts for product variants
    quantity threshold discounts Odoo
    flexible sales pricing by product template
    advanced discount logic for variants
    product template level discounting
    cross-variant quantity discounts
    scalable pricelist discounting
    Odoo sales pricing optimization tool
    variant aggregation for price calculation
    cumulative discount engine for Odoo
    unified pricing across product variants
    Odoo custom pricelist development
    bulk pricing by product template
    optimize sales pricing with cumulative discounts
            
    """,
    "description": """
        The Cumulative Pricelist by Product Template module extends Odoo's standard pricelist functionality
        by enabling quantity-based discount tiers to be applied cumulatively across all variants of the
        same product template.
        
        Instead of calculating discounts per individual variant, the system aggregates the total quantity
        of all variants under a product template to determine the applicable price tier. This ensures
        consistent and fair pricing for multi-variant products, such as different sizes, colors, or materials.
        
    cumulative pricelist by product template
    cumulative quantity discounts
    product variant quantity discount
    dynamic pricing by product template
    Odoo cumulative pricelist module
    quantity-based tiered pricing Odoo
    product template discount aggregation
    multi-variant cumulative pricing
    Odoo pricelist quantity discount
    cumulative pricing for product variants
    cumulative discount pricing Odoo
    tiered pricing across product variants
    quantity discount automation Odoo
    apply discounts by product template
    multi-variant discount pricing strategy
    Odoo sales pricelist customization
    volume pricing for product variants
    aggregate variant quantities for discount
    Odoo product pricing optimization
    advanced pricelist rules Odoo
    cumulative quantity discount management
    price breaks for product templates
    discount tiers based on combined quantity
    flexible pricelist discounts Odoo
    Odoo sales order pricing rules
    cumulative pricing rules for variants
    discount pricing across product variants
    Odoo pricing module for product templates
    automated tiered discounts Odoo
    product bundle pricing by template
    cumulative price breaks in sales orders
    managing discounts for product variants
    quantity threshold discounts Odoo
    flexible sales pricing by product template
    advanced discount logic for variants
    product template level discounting
    cross-variant quantity discounts
    scalable pricelist discounting
    Odoo sales pricing optimization tool
    variant aggregation for price calculation
    cumulative discount engine for Odoo
    unified pricing across product variants
    Odoo custom pricelist development
    bulk pricing by product template
    optimize sales pricing with cumulative discounts
            
    """,

    "version": "19.0.0.0",
    "category": "Sales/Pricing",
    "author": "TechUltra Solutions Private Limited",
    'company': 'TechUltra Solutions Private Limited',
    "website": "www.techultrasolutions.com",
    "depends": ["sale_management", "website_sale"],  # website_sale optional but useful for cart parity
    "data": [
        "views/product_pricelist_views.xml",
        "security/ir.model.access.csv",
    ],
    "assets": {
        # no frontend assets needed; website cart uses server-side pricing
    },
    "images": [
        "static/description/main_screen.gif",
    ],
    "currency": "USD",
    "price": 20,
    "license": "OPL-1",
    "installable": True,
    "application": True,
    "auto_install": False,
}
