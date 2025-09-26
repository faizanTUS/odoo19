# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Partner Last Order Info',
    'version': '19.0',
    'summary': """Display last confirmed sale and purchase orders with dates on partner form view.
    
        tus
        techultra
        techultra_private_limited_solution
        sale
        sale order
        purchase
        purchase order
        last sale
        last sale order
        last sale order history
        last purchase
        last purchase order
        last purchase order history
        last sale and purchase order
        last sale order on partner form
        last purchase order display
        partner form recent orders
        show last confirmed sale and purchase order
        contact view sale order history
        automatic order update on partner
        module show order history on partner
        Odoo last sale order on partner form
        Odoo last purchase order display
        Odoo partner form recent orders
        Odoo show last confirmed sale and purchase order
        Odoo contact view sale order history
        Odoo vendor profile last purchase order
        Odoo customer form recent transactions
        Odoo automatic order update on partner
        Odoo module show order history on partner
        Odoo CRM sale and purchase order integration
        Odoo last sale order
        Odoo last purchase order        
        Odoo partner form sale order        
        Odoo partner purchase order        
        Odoo customer last order        
        Odoo vendor last PO        
        Odoo contact order history               
        Odoo purchase tracking module        
        Partner transaction history Odoo
        Odoo sales automation module
        Odoo procurement enhancement
        Odoo B2B customer order tracking
        Odoo supplier order overview
        Odoo contact management improvement
        Odoo order management plugin
        Display SO PO info on contact view
        Odoo user rights for order visibility
        Odoo custom field order tracking
    """,
    'description': """
        This module displays the last confirmed Sale and Purchase Order along with their confirmation dates on the partner form view.
        Helps in quickly reviewing recent transactions with customers and vendors.
        
        Key Features:
        - Show last confirmed Sale Order with date
        - Show last confirmed Purchase Order with date
        - Visible directly on partner form
        
        
        tus
        techultra
        techultra_private_limited_solution
        sale
        sale order
        purchase
        purchase order
        last sale
        last sale order
        last sale order history
        last purchase
        last purchase order
        last purchase order history
        last sale and purchase order
        last sale order on partner form
        last purchase order display
        partner form recent orders
        show last confirmed sale and purchase order
        contact view sale order history
        automatic order update on partner
        module show order history on partner
        Odoo last sale order on partner form
        Odoo last purchase order display
        Odoo partner form recent orders
        Odoo show last confirmed sale and purchase order
        Odoo contact view sale order history
        Odoo vendor profile last purchase order
        Odoo customer form recent transactions
        Odoo automatic order update on partner
        Odoo module show order history on partner
        Odoo last sale order
        Odoo last purchase order        
        Odoo partner form sale order        
        Odoo partner purchase order        
        Odoo customer last order        
        Odoo vendor last PO        
        Odoo contact order history        
        Odoo CRM sale order integration        
        Odoo purchase tracking module        
        Partner transaction history Odoo
        Odoo sales automation module
        Odoo procurement enhancement
        Odoo B2B customer order tracking
        Odoo supplier order overview
        Odoo contact management improvement
        Odoo order management plugin
        Display SO PO info on contact view
        Odoo user rights for order visibility
        Odoo custom field order tracking

    """,
    'category': 'Sales/Purchases/Contact',
    'author': 'Techultra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'depends': ['base', 'contacts', 'sale', 'purchase'],
    'data': [
        'security/last_order_security.xml',
        'views/res_partner_views.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': False,
}