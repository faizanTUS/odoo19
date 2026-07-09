# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'POS Multi Cashier Management | POS Cashier Access Control',
    'version': '19.0.0.0',
    'category': 'Point Of Sale',
    'author': 'TechUltra Solutions Private Limited',
    'license': 'OPL-1',
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com/',
    'summary': """
    Assign cashiers to specific product categories to streamline POS operations, improve staff accountability, and ensure products are handled by the appropriate personnel.
    Assign Cashier by Product Category in Odoo
    Odoo POS Multi Cashier Management
    POS Cashier Access Control for Odoo
    Product Category Based Cashier Assignment
    Odoo POS User Restriction by Category
    Multi Cashier Selection in Odoo POS
    POS Cashier Permission Management
    Odoo POS Employee Access Management
    Category Wise Cashier Control
    Advanced POS Cashier Management
    Odoo POS Access Control
    Odoo Point of Sale Management
    Odoo POS User Restriction
    Odoo POS Employee Management
    Odoo POS Security
    Odoo Cashier Permissions
    Odoo POS Cashier Rights
    Odoo Retail Management
    POS Multi Cashier
    POS Cashier Management
    POS Cashier Access Control
    Odoo POS Cashier Management
    Multi Cashier POS
    POS Cashier Assignment
    POS Cashier Control
    Point of Sale Cashier Management
    Odoo POS Cashier Assignment
    POS User Access Control
    POS multi-cashier selection
    Odoo POS cashier assignment
    POS category-based cashier
    Odoo POS cashier control
    Multi-cashier POS system
    POS cashier by product category
    Assign cashiers to product categories
    Odoo POS retail management
    POS cashier restriction module
    Efficient cashier management in POS
    Odoo retail store POS customization
    Supermarket POS cashier ap
    """,
    'description': """
        POS Multi Cashier Management | POS Cashier Access Control enhances Odoo Point of Sale by enabling businesses to assign specific cashiers to designated product categories. This helps organizations manage cashier responsibilities more effectively while ensuring that sales transactions are handled by the appropriate personnel.
        Assign Cashier by Product Category in Odoo
    Odoo POS Multi Cashier Management
    POS Cashier Access Control for Odoo
    Product Category Based Cashier Assignment
    Odoo POS User Restriction by Category
    Multi Cashier Selection in Odoo POS
    POS Cashier Permission Management
    Odoo POS Employee Access Management
    Category Wise Cashier Control
    Advanced POS Cashier Management
    Odoo POS Access Control
    Odoo Point of Sale Management
    Odoo POS User Restriction
    Odoo POS Employee Management
    Odoo POS Security
    Odoo Cashier Permissions
    Odoo POS Cashier Rights
    Odoo Retail Management
    POS Multi Cashier
    POS Cashier Management
    POS Cashier Access Control
    Odoo POS Cashier Management
    Multi Cashier POS
    POS Cashier Assignment
    POS Cashier Control
    Point of Sale Cashier Management
    Odoo POS Cashier Assignment
    POS User Access Control
    POS multi-cashier selection
    Odoo POS cashier assignment
    POS category-based cashier
    Odoo POS cashier control
    Multi-cashier POS system
    POS cashier by product category
    Assign cashiers to product categories
    Odoo POS retail management
    POS cashier restriction module
    Efficient cashier management in POS
    Odoo retail store POS customization
    Supermarket POS cashier ap
    """,
    'depends': ['point_of_sale', 'pos_hr'],
    'data': [
        'views/pos_config_views.xml',
        'views/pos_order_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'tus_pos_orderline_cashier/static/src/app/cashier_button/cashier.xml',
            'tus_pos_orderline_cashier/static/src/app/cashier_button/orderline.xml',
            'tus_pos_orderline_cashier/static/src/overrides/models/model.js',
            'tus_pos_orderline_cashier/static/src/overrides/orderrecipt.js',
            'tus_pos_orderline_cashier/static/src/app/cashier_button/cashier.js',
            'tus_pos_orderline_cashier/static/src/app/cashier_button/orderline.js',
            'tus_pos_orderline_cashier/static/src/app/cashier_button/pos_load_hr_employe.js',
        ],
    },
    'images': [
        'static/description/icon.png',
    ],
    'price': 12.97,
    'currency': 'USD',
    'installable': True,
    'application': False,
    'auto_install': False,
}
