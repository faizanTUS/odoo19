# See LICENSE file for full copyright and licensing details.
{
    'name': 'Restrict Product and Category Access for Users',
    'version': '19.0.0.0',
    'category': 'Sales',
    'summary': """Restrict users to access only allowed products or categories
                Odoo restrict product access
                Odoo restrict category access 
                user-based product visibility Odoo
                product access rights
                product and category access control
                limited product view Odoo.
                Odoo Restrict Category Access
                Product Visibility Control Odoo
                Odoo Product Access Rights
                Odoo Category Access Restriction
                Odoo User-Based Product Access
                Restrict Products by User Odoo
                Odoo Product Access Management
                Category Access Control Odoo
                Odoo Limited Product View
                Odoo user permission for products and categories
                Control product access per user in Odoo
                Hide products from specific users Odoo
                Allow product/category access by user in Odoo
                Manage product and category access rights Odoo
                Odoo restrict product catalog by user
                Product-level security in Odoo
                Odoo product access based on roles
                Category filtering by user permission Odoo
                Odoo product permission settings
                User access control in Odoo
                Role-based product visibility
                Odoo data access restriction
                Odoo backend user permissions
                Secure product catalog in Odoo
                """,
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'depends': ['base', 'product'],
    'description': """
        The Restrict Product and Category Access for Users module for Odoo allows administrators to manage product
        visibility based on user permissions. Using the Allow Product and Allow Category options, admins can restrict
        access to specific products and categories, ensuring users only see what they are authorized to view.
        Odoo restrict product access
        Odoo restrict category access 
        user-based product visibility Odoo
        product access rights
        product and category access control
        limited product view Odoo.
        Odoo Restrict Category Access
        Product Visibility Control Odoo
        Odoo Product Access Rights
        Odoo Category Access Restriction
        Odoo User-Based Product Access
        Restrict Products by User Odoo
        Odoo Product Access Management
        Category Access Control Odoo
        Odoo Limited Product View
        Odoo user permission for products and categories
        Control product access per user in Odoo
        Hide products from specific users Odoo
        Allow product/category access by user in Odoo
        Manage product and category access rights Odoo
        Odoo restrict product catalog by user
        Product-level security in Odoo
        Odoo product access based on roles
        Category filtering by user permission Odoo
        Odoo product permission settings
        User access control in Odoo
        Role-based product visibility
        Odoo data access restriction
        Odoo backend user permissions
        Secure product catalog in Odoo
    """,
    'data': [
        # 'security/ir.model.access.csv',
        'security/product_restriction_rules.xml',
        'views/res_users_views.xml',
    ],
    "images": [
        "static/description/main_screen.gif"
    ],
    "currency": "USD",
    "price": 10,
    'license': 'OPL-1',
    "installable": True,
    "auto_install": False,
    "application": False,
}
