# See LICENSE file for full copyright and licensing details.
{
    "name": "Sample Bag",
    "version": "19.0.0.0",
    "category": "Sales",
    "author": "TechUltra Solutions Private Limited",
    'company': 'TechUltra Solutions Private Limited',
    "website": "www.techultrasolutions.com",
    "summary": """ Offering sample products is one of the most effective methods to connect with your
        target market. Customers will use these products and provide honest reviews, which is
        the best strategy for word-of-mouth promotion and increasing the popularity of your goods.
        Many companies may find it difficult to maintain and track sample products.Techultra has
        saved precious time by developing this multifunctional Sample bag app, which will help businesses
        and salesperson in doing their responsibilities smoothly.
        Odoo Sample Product Management
        Odoo Sample Bag App
        Product Sampling Tool Odoo
        Sample Tracking App Odoo
        Odoo Sample Product Tracking
        Manage Sample Products Odoo
        Odoo Sales Sample Module
        Odoo Product Demo Management
        Sample Product Distribution Odoo
        Techultra Sample Bag Module
        Odoo module for managing sample products
        Track product samples for sales team Odoo
        Salesperson sample product app Odoo
        Product sample bag management system
        Customer feedback sample product Odoo
        Odoo sample inventory control
        Product demo distribution Odoo ERP
        Sales sample tracking and review management
        Efficient sample product allocation in Odoo
        Monitor and control sample bags in Odoo
        Sample product review management
        Word-of-mouth marketing tools
        Customer engagement through samples
        Odoo sales automation for samples
        Odoo ERP product demo feature
        Track giveaways and sample items
        Product feedback workflow in Odoo
        Field sales sample monitoring
        ERP for sample marketing
        Demo product lifecycle management

         """,
    "description": """
        Offering sample products is one of the most effective methods to connect with your
        target market. Customers will use these products and provide honest reviews, which is
        the best strategy for word-of-mouth promotion and increasing the popularity of your goods.
        Many companies may find it difficult to maintain and track sample products.Techultra has
        saved precious time by developing this multifunctional Sample bag app, which will help businesses
        and salesperson in doing their responsibilities smoothly.

        Sample Bag
        Sales Manager
        Salesperson
        Sales person
        Stock
        Inventory
        Odoo Sales
        Sales team
        User Sample
        Sales Sample Bag
        Odoo Erp
        Sales sample bag
        Odoo Sample Product Management
        Odoo Sample Bag App
        Product Sampling Tool Odoo
        Sample Tracking App Odoo
        Odoo Sample Product Tracking
        Manage Sample Products Odoo
        Odoo Sales Sample Module
        Odoo Product Demo Management
        Sample Product Distribution Odoo
        Techultra Sample Bag Module
        Odoo module for managing sample products
        Track product samples for sales team Odoo
        Salesperson sample product app Odoo
        Product sample bag management system
        Customer feedback sample product Odoo
        Odoo sample inventory control
        Product demo distribution Odoo ERP
        Sales sample tracking and review management
        Efficient sample product allocation in Odoo
        Monitor and control sample bags in Odoo
        Sample product review management
        Word-of-mouth marketing tools
        Customer engagement through samples
        Odoo sales automation for samples
        Odoo ERP product demo feature
        Track giveaways and sample items
        Product feedback workflow in Odoo
        Field sales sample monitoring
        ERP for sample marketing
        Demo product lifecycle management

    """,
    "depends": [
        "sale_management",
        "sale",
        "stock",
        "sale_stock",
        "product",
        "l10n_in_sale_stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sample_bag_sequence.xml",
        "wizard/salesperson_update_views.xml",
        "wizard/sample_bag_create_so_views.xml",
        "wizard/sample_bag_from_so_views.xml",
        "wizard/scrap_quantity.xml",
        "wizard/warehouse_transfer_from_sb_views.xml",
        "views/sample_bag_views.xml",
        "views/sale_order_views_inherit.xml",
        "views/stock_warehouse_views_inherit.xml",
        "views/stock_picking_views_inherit.xml",
        "views/product_product_inherit_views.xml",
        "views/res_config_settings_inherit.xml",
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    "currency": "USD",
    "price": 29,
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "OPL-1",
}
