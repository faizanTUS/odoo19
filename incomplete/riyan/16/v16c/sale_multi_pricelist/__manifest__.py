# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
{
    'name': 'Sales Multi Pricelist | Compare & Apply Multiple Pricelists Per Order Line',
    'version': '16.0.0.0',
    'category': 'Sales',
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'summary': """Apply different pricelists per quotation line with instant preview and comparison
    
    
    tus
    techultra
    techultra_private_limited_solution
    Sales Multi Pricelist | Compare & Apply Multiple Pricelists Per Order Line
    multi pricelist
    multiple pricelist
    sale order pricelist
    pricelist per order line
    pricelist per product line
    sales pricelist comparison
    compare pricelists
    multi pricelist comparison
    pricelist comparison tool
    sale order pricelist
    pricelist wizard
    multiple pricelists
    pricelist per order line
    best price selector
    pricelist management
    sales pricing tool
    pricelist discount comparison
    sale
    order line
    order pricelist
    pricelist per order line
    pricelist per product line
    pricelist
    advanced pricing
    dynamic pricing
    sales price management
    flexible pricing
    line level pricing
    pricing rules
    product pricing rules
    sales discount
    automatic discount
    discount calculation
    discount by pricelist
    pricing strategy
    customer specific pricing
    b2b pricing
    wholesale pricing
    retail pricing
    bulk pricing
    quantity based pricing
    minimum quantity pricing
    tier pricing
    price comparison wizard
    sales order pricing control
    price optimization
    profit margin control
    sales price selector
    pricing flexibility
    multi pricing strategy
    product price override
    line price override
    sales workflow enhancement
    sales efficiency tool
    pricing automation
    price rule engine
    advanced sales pricing
    sales quotation pricing
    quotation price comparison
    multi currency pricing
    currency conversion pricing
    company specific pricing
    global pricing rules
    category based pricing
    product variant pricing
    template based pricing
    sales line pricing
    pricing accuracy
    pricing transparency
    sales pricing extension
    pricing management tool
    advanced discount management
    sales team productivity
    pricing comparison tool
    dynamic sale pricing
    compare pricelists on sale order
    apply different pricelist per line
    pricelist comparison wizard
    sale order line pricelist
    multi pricelist on order
    pricelist discount comparison tool
    best pricelist selector
    pricelist price comparison tool
    select pricelist per product
    line level pricelist selection
    pricelist switching tool
    dynamic pricelist selection
    discount comparison wizard
    sales order pricing management
    pricelist rule comparison tool
    discount amount comparison
    minimum quantity pricelist
    pricelist currency conversion
    multi currency pricelist
    one click pricelist apply
    price rule comparison
    product price comparison
    sales discount management
    pricelist automation tool
    smart pricing selector
    B2B pricing management
    wholesale pricelist management
    retail pricing tool
    customer segment pricing
    regional pricelist management
    seasonal pricing management
    sales team pricing tool
    ERP pricelist module
    sales pricing optimization
    pricing strategy management
    ERP multi pricelist module
    sales order pricing module
    pricelist comparison app
    enterprise pricelist tool
    multi pricelist comparison module 
    
    """,
    'description': """
Sale Multi Pricelist on Order
=============================

Allows sales users to apply different pricelists on each quotation line while
keeping the standard sales workflow unchanged.
Compare all pricelists side-by-side on each sale order line and apply the best price in one click - with discount amounts shown instantly.

Features
--------
* **Per-line pricelist**: Set a specific pricelist on each order line; when not set, the order's pricelist is used.
* **Instant preview**: Changing a line's pricelist updates the unit price and totals immediately.
* **Multi Pricelist pop-up**: Compare prices across all available pricelists for a product and apply the best one.
* **Accurate calculations**: Currency rules, taxes, and order totals are updated automatically.
* **Safe and flexible**: No page refresh; works with existing discount and tax logic.


    tus
    techultra
    techultra_private_limited_solution
    Sales Multi Pricelist | Compare & Apply Multiple Pricelists Per Order Line
    multi pricelist
    multiple pricelist
    sale order pricelist
    pricelist per order line
    pricelist per product line
    sales pricelist comparison
    compare pricelists
    multi pricelist comparison
    pricelist comparison tool
    sale order pricelist
    pricelist wizard
    multiple pricelists
    pricelist per order line
    best price selector
    pricelist management
    sales pricing tool
    pricelist discount comparison
    sale
    order line
    order pricelist
    pricelist per order line
    pricelist per product line
    pricelist
    advanced pricing
    dynamic pricing
    sales price management
    flexible pricing
    line level pricing
    pricing rules
    product pricing rules
    sales discount
    automatic discount
    discount calculation
    discount by pricelist
    pricing strategy
    customer specific pricing
    b2b pricing
    wholesale pricing
    retail pricing
    bulk pricing
    quantity based pricing
    minimum quantity pricing
    tier pricing
    price comparison wizard
    sales order pricing control
    price optimization
    profit margin control
    sales price selector
    pricing flexibility
    multi pricing strategy
    product price override
    line price override
    sales workflow enhancement
    sales efficiency tool
    pricing automation
    price rule engine
    advanced sales pricing
    sales quotation pricing
    quotation price comparison
    multi currency pricing
    currency conversion pricing
    company specific pricing
    global pricing rules
    category based pricing
    product variant pricing
    template based pricing
    sales line pricing
    pricing accuracy
    pricing transparency
    sales pricing extension
    pricing management tool
    advanced discount management
    sales team productivity
    pricing comparison tool
    dynamic sale pricing
    compare pricelists on sale order
    apply different pricelist per line
    pricelist comparison wizard
    sale order line pricelist
    multi pricelist on order
    pricelist discount comparison tool
    best pricelist selector
    pricelist price comparison tool
    select pricelist per product
    line level pricelist selection
    pricelist switching tool
    dynamic pricelist selection
    discount comparison wizard
    sales order pricing management
    pricelist rule comparison tool
    discount amount comparison
    minimum quantity pricelist
    pricelist currency conversion
    multi currency pricelist
    one click pricelist apply
    price rule comparison
    product price comparison
    sales discount management
    pricelist automation tool
    smart pricing selector
    B2B pricing management
    wholesale pricelist management
    retail pricing tool
    customer segment pricing
    regional pricelist management
    seasonal pricing management
    sales team pricing tool
    ERP pricelist module
    sales pricing optimization
    pricing strategy management
    ERP multi pricelist module
    sales order pricing module
    pricelist comparison app
    enterprise pricelist tool
    multi pricelist comparison module 
    """,
    'depends': ['sale'],
    'data': [
        "security/res_groups_view.xml",
        'security/ir.model.access.csv',
        'wizard/sale_multi_pricelist_wizard_views.xml',
        'views/sale_order_views.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'currency': 'USD',
    'price': 14.90,
    "license": "OPL-1",
    "installable": True,
    "application": True,
    "auto_install": False,
}
