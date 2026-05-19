# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': "User Warehouse Access Control | Stock Location Restriction",
    'version': '18.0.0.0',
    'category': 'Inventory/Stock',
    'summary': """User-level restrictions for warehouses, locations, picking types, and sale order limits.
            
        tus
        techultra
        techultra_private_limited_solution
        Warehouse Stock Restrictions
        Warehouse Restriction for User | Stock Location Restriction
        Sale Order Limit
        sale limit
        limit
        Stock
        stock
        warehouse
        Warehouse
        restriction
        sale
        warehouse restriction
        stock location restriction
        picking type restriction
        warehouse access control
        inventory access restrictions
        sales restriction
        user access limit
        warehouse security
        odoo warehouse management
        stock move restriction
        Odoo warehouse restriction module
        Odoo warehouse access control
        Odoo restrict stock locations
        Odoo picking type restrictions
        Odoo warehouse security module
        Odoo user warehouse permission
        Odoo stock location restriction
        Odoo inventory restriction module
        Odoo sales warehouse restriction
        Odoo hide sale orders by warehouse
        Odoo restrict stock picking
        Odoo user-specific warehouse access
        Odoo operation type restriction
        Odoo stock move validation restriction
        Odoo warehouse security access control
        Odoo multi-warehouse access restriction
        Odoo warehouse user rights
        Odoo location-level restrictions
        Odoo stock movement access rules
        Odoo transfer validation control
        Odoo picking validation rule module
        Odoo role-based inventory control
        Odoo security rules for stock operations
        Odoo hide warehouses from users
        Odoo stock visibility restriction
        Odoo warehouse data access limit
        Odoo restricted user permissions inventory
        Odoo restrict stock operations
        Odoo product movement access control
        Odoo picking view restriction
        Odoo stock move domain rules
        ERP warehouse security
        Inventory access control system
        Multi-warehouse ERP management
        Warehouse data privacy solution
        ERP compliance for stock management
        Odoo sale order visibility restriction
        Odoo user-specific sale order filters
        Limit sale orders by user Odoo
        Odoo restricted partner sales visibility
        Odoo secure sale order management
        Warehouse restriction app
        Stock access control extension
        Odoo inventory security app
        User warehouse permission addon
        Stock visibility restriction tool
        Inventory privacy management module
        Multi-location control for Odoo
                
        
    """,
    'description': """
        Restrict user access to warehouses, stock locations, picking types,
        and limit the visibility of sale orders based on per-user settings.
        
        tus
        techultra
        techultra_private_limited_solution
        Warehouse Stock Restrictions
        Warehouse Restriction for User | Stock Location Restriction
        Sale Order Limit
        sale limit
        limit
        Stock
        stock
        warehouse
        Warehouse
        restriction
        sale
        warehouse restriction
        stock location restriction
        picking type restriction
        warehouse access control
        inventory access restrictions
        sales restriction
        user access limit
        warehouse security
        odoo warehouse management
        stock move restriction
        Odoo warehouse restriction module
        Odoo warehouse access control
        Odoo restrict stock locations
        Odoo picking type restrictions
        Odoo warehouse security module
        Odoo user warehouse permission
        Odoo stock location restriction
        Odoo inventory restriction module
        Odoo sales warehouse restriction
        Odoo hide sale orders by warehouse
        Odoo restrict stock picking
        Odoo user-specific warehouse access
        Odoo operation type restriction
        Odoo stock move validation restriction
        Odoo warehouse security access control
        Odoo multi-warehouse access restriction
        Odoo warehouse user rights
        Odoo location-level restrictions
        Odoo stock movement access rules
        Odoo transfer validation control
        Odoo picking validation rule module
        Odoo role-based inventory control
        Odoo security rules for stock operations
        Odoo hide warehouses from users
        Odoo stock visibility restriction
        Odoo warehouse data access limit
        Odoo restricted user permissions inventory
        Odoo restrict stock operations
        Odoo product movement access control
        Odoo picking view restriction
        Odoo stock move domain rules
        ERP warehouse security
        Inventory access control system
        Multi-warehouse ERP management
        Warehouse data privacy solution
        ERP compliance for stock management
        Odoo sale order visibility restriction
        Odoo user-specific sale order filters
        Limit sale orders by user Odoo
        Odoo restricted partner sales visibility
        Odoo secure sale order management
        Warehouse restriction app
        Stock access control extension
        Odoo inventory security app
        User warehouse permission addon
        Stock visibility restriction tool
        Inventory privacy management module
        Multi-location control for Odoo
        
    """,
    'author': 'Techultra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'license': 'OPL-1',
    'depends': [
        'base',
        'stock',
        'sale_stock',
        'sale_management',
        'contacts',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/users_view.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'currency': 'USD',
    'price': 16.99,
    'installable': True,
    'auto_install': False,
    'application': False,

}
