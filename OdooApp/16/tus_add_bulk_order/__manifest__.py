# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Add Bulk Products in SaleOrder',
    'version': '16.0.0.0',
    'author': 'Techultra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com/',
    'category': 'Sale',
    'summary': 'Search by model code and add many sale order lines with variant quantities, stock, and prices.',
    'description': 'Open a draft quotation, launch the bulk grid, pick product templates by model name, '
                   'review stock per variant, enter quantities and unit prices, then create sale order lines.',
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
