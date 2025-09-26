# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Handling Invoices Directly from Picking',
    'version': '19.0.0.0',
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'summary': """Handling invoices directly from picking operations
                Odoo Invoice from Picking
                Picking to Invoice Odoo
                Odoo Stock Picking Invoice Integration
                Odoo Invoice Creation from Delivery
                Odoo Invoicing from Operations
                Odoo Picking Invoice Workflow
                Odoo Delivery to Invoice Module
                Invoice on Delivery Odoo
                Odoo Stock to Invoice Automation
                Odoo Warehouse Invoicing Tool
                Create invoice from picking in Odoo
                Automate invoicing after delivery in Odoo
                Odoo picking operation invoice management
                Odoo generate invoice from stock picking
                Odoo warehouse to invoice integration
                Odoo invoice after goods delivery
                Stock delivery invoicing in Odoo
                Odoo logistics invoice flow
                Invoice based on delivery order Odoo
                Handle invoice from picking screen Odoo
                Warehouse and invoicing automation
                Odoo backend process integration
                Odoo logistics to finance workflow
                Delivery-based billing Odoo
                Real-time invoice generation Odoo
                Post-picking invoice process
                ERP delivery to billing sync
                Sales order fulfillment to invoice
                Streamlined stock invoicing
                Odoo stock module enhancements

    
    """,
    'description': """This module allows Handling invoices directly from picking operations in Odoo.
                        Odoo Invoice from Picking
                        Picking to Invoice Odoo
                        Odoo Stock Picking Invoice Integration
                        Odoo Invoice Creation from Delivery
                        Odoo Invoicing from Operations
                        Odoo Picking Invoice Workflow
                        Odoo Delivery to Invoice Module
                        Invoice on Delivery Odoo
                        Odoo Stock to Invoice Automation
                        Odoo Warehouse Invoicing Tool
                        Create invoice from picking in Odoo
                        Automate invoicing after delivery in Odoo
                        Odoo picking operation invoice management
                        Odoo generate invoice from stock picking
                        Odoo warehouse to invoice integration
                        Odoo invoice after goods delivery
                        Stock delivery invoicing in Odoo
                        Odoo logistics invoice flow
                        Invoice based on delivery order Odoo
                        Handle invoice from picking screen Odoo
                        Warehouse and invoicing automation
                        Odoo backend process integration
                        Odoo logistics to finance workflow
                        Delivery-based billing Odoo
                        Real-time invoice generation Odoo
                        Post-picking invoice process
                        ERP delivery to billing sync
                        Sales order fulfillment to invoice
                        Streamlined stock invoicing
                        Odoo stock module enhancements

    """,
    'category': 'tool',
    'license': 'OPL-1',
    'depends': ['stock', 'account','sale'],
    'data': [
        'views/stock_picking_views.xml',
        'views/account_move_views.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 12.00,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': True,
}
