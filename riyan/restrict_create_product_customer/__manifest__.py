# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    "name": "Restrict Create Product, Product Variants & Customer",
    "version": "19.0.0.0",
    "depends": ["base",'sale', 'sale_management', "product"],
    "author": "Techultra Solutions Private Limited",
    'website': "https://www.techultrasolutions.com/",
    "category": "Security",
    "description": '''
    Restricts users from creating Products and Partners unless they have specific permissions.

    tus 
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited
    odoo 19
    Restrict Create Product
    Restrict Product Variants
    Restrict Create Customer
    Product Creation Restriction
    Customer Creation Control
    Product Variant Access Control
    User Access Restriction
    Odoo Product Variant Security
    Disable Create Button
    Restrict Product Creation Odoo
    Control Product Variant Creation
    Restrict Customer Entry
    Prevent Duplicate Records Odoo
    Product Management Security
    Access Rights for Product Creation
    Customer Data Control
    Streamline Product Entry
    Odoo Product Variant Restriction
    User Permission Product Creation
    Odoo Security Module
    Odoo Access Restriction
    Product Creation Permission
    Customer Record Restriction
    Disable Add Product Button
    Limit Product Variant Creation
    Product Security Rules
    Odoo User Role Management
    Restrict Salesperson Access
    Control Master Data Creation
    Product Variant Entry Control
    Prevent Unauthorized Product Creation
    Create Rights Management
    Odoo User Restriction Module
    Block Product Add Button
    Customer Access Management
    Odoo Master Data Security
    Hide Create Button in Form View
    Limit Data Creation in Odoo
    Product and Customer Entry Control
    Secure Product Management
    Access Control for Product Variant
    Restrict Create Option Odoo
    Prevent Duplicate Customer Records
    Product Variant Creation Workflow
    Admin Only Product Creation
    Role-Based Product Management
    Controlled Data Entry Module
    Master Record Creation Control
    No Product Creation for Employees
    Odoo Permission Restriction Tool
    ''',
    "data": [
        "security/restrict_create_rules.xml",
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'assets': {
        'web.assets_backend': [
            'restrict_create_product_customer/static/src/xml/button.js',
            'restrict_create_product_customer/static/src/xml/button.xml',
        ],
    },
    "installable": True,
    'license': 'OPL-1',
    "application": False,
}
