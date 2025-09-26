# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Add Bulk Products in SaleOrder',
    'version': '19.0',
    'author': 'Techultra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'category': 'Sale',
    'summary': """ Add Bulk Product in Sale Order 
    
    tus
    techultra
    techultra_private_limited_solution
    odoo sale order
    multi product in sale order
    sale order product
    products
    multi products
    Bulk Product Addition
    Sale Order Automation
    Add Products in Bulk
    Product Variants Management
    Streamline Sale Orders
    Bulk Order Processing
    Efficient Sale Order Creation
    Product Variant Selection
    Time-Saving Sales Tool
    Sales Order Management
    Order Creation Automation
    Real-Time Stock Updates
    Add Multiple Products Quickly
    Efficient Inventory Management
    Bulk Order Add-on
    Bulk Sales Tool
    odoo
    odoo16
    odoo17
    odoo18
    Sales Order Bulk Upload
    Efficient Order Processing
    Multi-Product Addition
    Variant-based Product Selection
    Large Scale Order Management
    Quick Sale Order Creation
    Streamlined Order Processing
    Advanced Product Management
    Real-Time Order Management
    Inventory-Based Order Creation
    Bulk Product Search and Add
    Product Variants Quick Add
    Automated Sales Order Tool
    Sales Order Workflow Optimization
    Efficient Inventory Sales
    Fast Product Addition Tool
    Order Management Automation
    Simplified Sales Order Creation
    Bulk Product Entry Tool    
    Fast Product Addition to Orders
    Quick Order Management
    Multi-Variant Product Order    
    Bulk Product Import for Sales    
    Order Creation Software    
    Bulk Order Creation    
    Fast Product Variant Selection    
    Sales Order Bulk Update    
    Automated Product Addition    
    Efficient Bulk Sales Tool    
    Time-Saving Order Management    
    Simplified Sales Order Processing    
    Multi-Product Variant Entry    
    Bulk Order Workflow    
    Large Batch Order Creation    
    Product Bulk Selection    
    Variant-Based Order Creation    
    Product List for Orders    
    Sales Order Efficiency Tool    
    Quick Inventory Order Management    
    Smart Bulk Product Upload    
    Fast Order Creation Process    
    Bulk Order Entry Tool    
    Order Management System    
    Bulk Inventory Management for Sales    
    Order Processing Made Easy    
    Bulk Sales Order Entry    
    Instant Product Addition to Orders    
    Bulk Inventory Upload for Sales    
    Simple Order Entry System      
      
    """,
    'description': """Add Bulk Product in Sale Order
    
    tus
    techultra
    techultra_private_limited_solution
    odoo sale order
    multi product in sale order
    sale order product
    products
    multi products
    Bulk Product Addition
    Sale Order Automation
    Add Products in Bulk
    Product Variants Management
    Streamline Sale Orders
    Bulk Order Processing
    Efficient Sale Order Creation
    Product Variant Selection
    Time-Saving Sales Tool
    Sales Order Management
    Order Creation Automation
    Real-Time Stock Updates
    Add Multiple Products Quickly
    Efficient Inventory Management
    Bulk Order Add-on
    Bulk Sales Tool
    odoo
    odoo16
    odoo17
    odoo18
    Sales Order Bulk Upload
    Efficient Order Processing
    Multi-Product Addition
    Variant-based Product Selection
    Large Scale Order Management
    Quick Sale Order Creation
    Streamlined Order Processing
    Advanced Product Management
    Real-Time Order Management
    Inventory-Based Order Creation
    Bulk Product Search and Add
    Product Variants Quick Add
    Automated Sales Order Tool
    Sales Order Workflow Optimization
    Efficient Inventory Sales
    Fast Product Addition Tool
    Order Management Automation
    Simplified Sales Order Creation
    Bulk Product Entry Tool    
    Fast Product Addition to Orders
    Quick Order Management
    Multi-Variant Product Order    
    Bulk Product Import for Sales    
    Order Creation Software    
    Bulk Order Creation    
    Fast Product Variant Selection    
    Sales Order Bulk Update    
    Automated Product Addition    
    Efficient Bulk Sales Tool    
    Time-Saving Order Management    
    Simplified Sales Order Processing    
    Multi-Product Variant Entry    
    Bulk Order Workflow    
    Large Batch Order Creation    
    Product Bulk Selection    
    Variant-Based Order Creation    
    Product List for Orders    
    Sales Order Efficiency Tool    
    Quick Inventory Order Management    
    Smart Bulk Product Upload    
    Fast Order Creation Process    
    Bulk Order Entry Tool    
    Order Management System    
    Bulk Inventory Management for Sales    
    Order Processing Made Easy    
    Bulk Sales Order Entry    
    Instant Product Addition to Orders    
    Bulk Inventory Upload for Sales    
    Simple Order Entry System      
    
    """,
    'depends': ['base', 'sale_management', 'stock'],
    'data': [
        "wizard/bulk_order_wizard_view.xml",
        "views/product_template_views.xml",
        "views/sale_order.xml",
    ],
    'assets': {
        'web.assets_backend': [
            "tus_add_bulk_order/static/src/css/style.css",
            'tus_add_bulk_order/static/src/BulkOrder/bulk_order_grid.js',
            'tus_add_bulk_order/static/src/BulkOrder/bulk_order_grid_template.xml',
        ],
    },
    "images": [
        "static/description/main_screen.gif",
    ],
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    'price': 20.00,
    'currency': 'EUR',
}
