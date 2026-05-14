# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Bulk Add Products to Sale Order | Mass Product & Variant Selector for Odoo',
    'version': '16.0.0.0',
    'author': 'Techultra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com/',
    'category': 'Sale',
    'summary': 'Quickly add multiple products and variants to Odoo Sale Orders with bulk selection, quantity management, and real-time stock visibility.',
    'description': """

    Bulk Add Products to Sale Order for Odoo

    The Bulk Add Products to Sale Order module helps sales teams quickly create large sale orders by allowing users to add multiple products and variants in a single step.

    Instead of manually adding products one by one, users can search, filter, and select multiple items with quantities directly from a smart bulk product selection wizard.

    This module is designed for wholesalers, distributors, retailers, trading companies, and businesses handling high-volume sales operations in Odoo.

    Key Features
    ============

    * Add multiple products and variants into Sale Orders instantly
    * Bulk product selection with advanced search functionality
    * Search and select products by name, SKU, or variant attributes
    * Enter quantities for multiple product variants in one screen
    * View real-time stock availability before adding products
    * Automatically create Sale Order lines from selected products
    * Reduce manual order entry work and save valuable time
    * Minimize product selection and quantity entry errors
    * Improve sales team productivity and order processing speed
    * Fully integrated with the standard Odoo Sale Order workflow
    * User-friendly interface for quick adoption by sales teams
    * Ideal for wholesale, bulk, and B2B order processing

    Business Benefits
    =================

    * Faster Sale Order creation
    * Better operational efficiency
    * Reduced manual data entry
    * Improved order accuracy
    * Streamlined bulk sales workflow
    * Better visibility of available stock
    * Suitable for high-volume sales teams

    Supported Versions
    ==================

    * Odoo 16

    Industries
    ==========

    * Wholesale
    * Retail
    * Distribution
    * Manufacturing
    * Trading Companies
    * B2B Sales Operations

    SEO Keywords
    ============

    odoo bulk sale order, odoo add multiple products, odoo sale order bulk products,
    odoo bulk product selection, odoo sales order automation, odoo variant selection,
    odoo bulk order entry, odoo mass product add, odoo wholesale order management,
    odoo product variant order entry, odoo sale order productivity, odoo bulk sales tool

    """,
    'depends': ['base', 'sale_management', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/bulk_order_wizard_view.xml',
        'views/product_template_views.xml',
        'views/sale_order.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'tus_add_bulk_order/static/src/css/style.css',
            'tus_add_bulk_order/static/src/BulkOrder/bulk_order_grid.js',
            'tus_add_bulk_order/static/src/BulkOrder/bulk_order_grid_template.xml',
        ],
    },
    'images': [
        'static/description/main_screen.gif',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    'price': 20.00,
    'currency': 'EUR',
}
