# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Custom Pricelist Access',
    'version': '19.0',
    'company': 'TechUltra Solutions Private Limited',
    'summary': """Custom Pricelist Access restricts users to use only the pricelist assigned by the admin when creating sale orders, ensuring controlled and user - specific pricing.
        pricelist
        price
        CustomPricelistAccess
        OdooPricelist
        OdooAccessControl
        OdooCustomModule
        Odoo18
        OdooPricingRules
        PricelistPermissions
        OdooSalesCustomization
        OdooPricelistAccess
        OdooModuleDevelopment
        OdooApps
        OdooDevelopment
        OdooCustomization
        OdooModule
        OdooExtensions
        OdooAddons
        OdooSalesModule
        OdooPriceManagement
        OdooDiscountRules
        CustomPricingOdoo
        PriceAccessControl
        OdooUserAccess
        OdooAccessRights
        OdooPermissions
        RestrictPricelistAccess
        OdooUserGroups
        AccessControlOdoo
        ManageOdooPrices
        OdooAdvancedPricing
        DynamicPricelists
        UserBasedPricelist
        Odoo17
        Odoo16
        TUS
        tus
        techultra solutions
        techultra
        techultra solutions private limited
        pricelist access
    """,
    'description': """
        Custom Pricelist Access allows admins to assign specific pricelists to individual users. When a user creates a sale order, only the assigned pricelist can be applied, preventing changes or access to other pricelists. This ensures accurate pricing control based on user roles. Admins can define multiple pricelists and map them to different users as needed. The module enhances sales security and simplifies pricelist management in multi-user environments.
        pricelist
        price
        CustomPricelistAccess
        OdooPricelist
        OdooAccessControl
        OdooCustomModule
        Odoo18
        OdooPricingRules
        PricelistPermissions
        OdooSalesCustomization
        OdooPricelistAccess
        OdooModuleDevelopment
        OdooApps
        OdooDevelopment
        OdooCustomization
        OdooModule
        OdooExtensions
        OdooAddons
        OdooSalesModule
        OdooPriceManagement
        OdooDiscountRules
        CustomPricingOdoo
        PriceAccessControl
        OdooUserAccess
        OdooAccessRights
        OdooPermissions
        RestrictPricelistAccess
        OdooUserGroups
        AccessControlOdoo
        ManageOdooPrices
        OdooAdvancedPricing
        DynamicPricelists
        UserBasedPricelist
        Odoo17
        Odoo16
        TUS
        tus
        techultra solutions
        techultra
        techultra solutions private limited
        pricelist access
        """,
    'category': 'Sales',
    'author': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com',
    'depends': ['product', 'sale_management'],
    'data': [
        'security/pricelist_restriction_rule.xml',
        'views/product_pricelist_view.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'license': 'OPL-1',
}
