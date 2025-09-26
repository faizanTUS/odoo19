# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    # App information
    'name': 'Markup Pricelist Range',
    'version': '19.0',
    'summary': """This feature helps businesses set flexible pricing based on cost by adjusting markup, rounding, and extra fees—enabling smarter, cost-driven pricing strategies
        OdooModule
        OdooCustomization
        OdooApps
        OdooDevelopment
        OdooPricelist
        OdooPricing
        OdooCostBasedPricing
        OdooMarkupPricing
        FormulaPricing
        PricingAutomation
        DynamicPricing
        CostBasedRules
        FlexiblePricing
        AdvancedPricelistOdoo
        MarkupPercentage
        OdooMarkupRules
        MinMaxCostControl
        AutoPricingStrategy
        PriceMarkupLogic
        BasedOnCostPrice
        Odoo17
        Odoo16
        Odoo18
        Odoo19
        TUS
        tus
        techultra solutions
        techultra
        techultra solutions private limited
        pricelist access
    """,
    'description': """
        This module "Markup Pricelist Range" enhances the standard pricelist rules by introducing a formula-based pricing option. When the user selects "Based on Cost Price", additional fields such as Minimum Cost, Maximum Cost, and Markup Percentage dynamically appear. These fields allow precise control over product pricing based on cost, enabling businesses to apply flexible and automated pricing strategies.
        OdooModule
        OdooCustomization
        OdooApps
        OdooDevelopment
        OdooPricelist
        OdooPricing
        OdooCostBasedPricing
        OdooMarkupPricing
        FormulaPricing
        PricingAutomation
        DynamicPricing
        CostBasedRules
        FlexiblePricing
        AdvancedPricelistOdoo
        MarkupPercentage
        OdooMarkupRules
        MinMaxCostControl
        AutoPricingStrategy
        PriceMarkupLogic
        BasedOnCostPrice
        Odoo17
        Odoo16
        Odoo18
        Odoo19
        TUS
        tus
        techultra solutions
        techultra
        techultra solutions private limited
        pricelist access
        """,
    # 'category': 'Hidden/Tools',
    'author': 'TechUltra Solutions Private Limited',
    "license": "LGPL-3",
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com/',
    # Dependencies
    'depends': ['product', 'sale_management', 'website_sale'],
    'data': [
        'views/cost_markup.xml',
        'views/product_template.xml',
    ],
    # Images and gifs
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 18.85,
    'currency': 'USD',
    # Technical
    'installable': True,
    'application': True,
    'auto_install': False,
}
