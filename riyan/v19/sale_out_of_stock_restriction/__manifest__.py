# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
{
    'name': 'Prevent Sale Order Confirmation for Out of Stock Products',
    'version': '19.0.0.0',
    'category': 'Sales/Sales',
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'summary': """
    Enforce stock availability rules on sales orders by preventing confirmation when ordered quantities exceed 
    available on-hand or forecast stock
    
    tus
    techultra
    techultra_private_limited_solution
    sale
    order
    restrict
    stock 
    product
    sale order
    out of stock
    quantity
    prevent out of stock sales
    block sale order out of stock
    sale order stock restriction
    stock validation for sales
    sale order stock control
    prevent overselling products
    stock availability validation
    block sales without stock
    sale order quantity validation
    inventory based sales control
    real time stock validation
    stock check before confirmation
    restrict sales by stock
    stop selling unavailable products
    stock enforcement for sales
    automatic stock validation
    sale order stock check
    inventory validation for orders
    stock level restriction
    prevent negative stock sales
    sales stock availability control
    block order confirmation no stock
    validate stock before sale
    stock based order restriction
    product availability validation
    sales inventory control system
    stock validation module
    order quantity stock check
    inventory rule enforcement
    stock control for sale orders
    real time inventory check
    sales order validation system
    stock availability control
    block order when no stock
    inventory accuracy control
    sales stock enforcement
    product stock validation
    order confirmation restriction
    stock driven sales process
    validate product quantity
    stock availability rule
    inventory check automation
    sales restriction by stock
    stock validation engine
    order stock verification
    product stock control system
    sales inventory validation
    stock check automation
    inventory restriction system
    order validation by stock
    stock control automation
    sales order restriction module
    product availability control
    stock validation rules
    inventory stock enforcement
    sales stock check system
    block insufficient stock orders
    validate inventory before sale
    stock restriction engine
    sales order stock rules
    inventory based order validation
    stock verification system
    product stock availability check
    sales validation by inventory
    order processing stock control
    inventory validation engine
    stock control for order processing
    prevent stock mismatch sales
    sales order stock verification
    inventory check before confirmation
    stock based validation system
    prevent out of stock sales
    block sale order out of stock
    sale order stock restriction
    stock validation for sales
    prevent overselling products
    block sales without stock
    sale order stock control
    real time stock validation
    stock availability validation
    sale order quantity validation
    stock check before confirmation
    restrict sales by stock
    stop selling unavailable products
    stock enforcement for sales
    inventory based sales control
    validate stock before sale
    block order when no stock
    sales stock availability control
    stock based order restriction
    inventory validation for orders
    product availability enforcement
    sales inventory rules
    stock validation for order confirmation
    order restriction by inventory
    inventory control for sales process
    """,
    'description': """
     This module adds a powerful validation layer to your Odoo Sales process. It prevents users from confirming sale
     orders when products are not available in stock.
     No more overselling. No more stock conflicts. Only accurate, reliable sales.
    
    
    tus
    techultra
    techultra_private_limited_solution
    sale
    order
    restrict
    stock 
    product
    sale order
    out of stock
    quantity
    prevent out of stock sales
    block sale order out of stock
    sale order stock restriction
    stock validation for sales
    sale order stock control
    prevent overselling products
    stock availability validation
    block sales without stock
    sale order quantity validation
    inventory based sales control
    real time stock validation
    stock check before confirmation
    restrict sales by stock
    stop selling unavailable products
    stock enforcement for sales
    automatic stock validation
    sale order stock check
    inventory validation for orders
    stock level restriction
    prevent negative stock sales
    sales stock availability control
    block order confirmation no stock
    validate stock before sale
    stock based order restriction
    product availability validation
    sales inventory control system
    stock validation module
    order quantity stock check
    inventory rule enforcement
    stock control for sale orders
    real time inventory check
    sales order validation system
    stock availability control
    block order when no stock
    inventory accuracy control
    sales stock enforcement
    product stock validation
    order confirmation restriction
    stock driven sales process
    validate product quantity
    stock availability rule
    inventory check automation
    sales restriction by stock
    stock validation engine
    order stock verification
    product stock control system
    sales inventory validation
    stock check automation
    inventory restriction system
    order validation by stock
    stock control automation
    sales order restriction module
    product availability control
    stock validation rules
    inventory stock enforcement
    sales stock check system
    block insufficient stock orders
    validate inventory before sale
    stock restriction engine
    sales order stock rules
    inventory based order validation
    stock verification system
    product stock availability check
    sales validation by inventory
    order processing stock control
    inventory validation engine
    prevent out of stock sales
    block sale order out of stock
    sale order stock restriction
    stock validation for sales
    prevent overselling products
    block sales without stock
    sale order stock control
    real time stock validation
    stock availability validation
    sale order quantity validation
    stock check before confirmation
    restrict sales by stock
    stop selling unavailable products
    stock enforcement for sales
    inventory based sales control
    validate stock before sale
    block order when no stock
    sales stock availability control
    stock based order restriction
    inventory validation for orders
    stock control for order processing
    prevent stock mismatch sales
    sales order stock verification
    inventory check before confirmation
    stock based validation system
    product availability enforcement
    sales inventory rules
    stock validation for order confirmation
    order restriction by inventory
    inventory control for sales process
    """,
    'depends': ['sale_stock'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/sale_order_views.xml',
    ],
    'images': [
        'static/description/main_screen.gif'
    ],
    'price': 13.00,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
