# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Purchase Discount Advanced',
    'version': '19.0.0.0',
    'author': 'Techultra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'category': 'Purchase',
    'summary': """Purchase Discount Advanced
        Easily apply percentage, global, or fixed amount discounts on purchase orders. This module automates discount calculation, integrates with vendor bills and reports, and includes role-based access control for secure and efficient procurement management.
        tus
        techultra
        techultra_private_limited_solution
        Odoo 19 purchase discount Advanced
        Odoo 18 purchase discount Advanced
        Odoo 17 purchase discount Advanced
        Odoo 16 purchase discount Advanced
        Odoo purchase global discount
        Odoo vendor discount module        
        Odoo purchase order discount wizard       
        Odoo fixed amount discount
        Odoo percentage discount on purchase        
        Odoo procurement discount management       
        Odoo purchase order PDF discount        
        Odoo supplier discount automation        
        Odoo 19 discount on purchase orders
        Odoo 18 discount on purchase orders
        Odoo 17 discount on purchase orders
        Odoo 16 discount on purchase orders
        Odoo 19 purchase global discount
        Odoo 18 purchase global discount
        Odoo 17 purchase global discount
        Odoo 16 purchase global discount
        Odoo purchase order discount module
        odoo
        odoo16
        odoo17
        odoo18
        odoo19
        Odoo procurement discount management
        Odoo vendor discount automation
        Odoo purchase order fixed discount
        Odoo purchase percentage discount
        Odoo supplier discount tool
        Odoo 19 purchase discount wizard
        Odoo 18 purchase discount wizard
        Odoo 17 purchase discount wizard
        Odoo 16 purchase discount wizard
        Odoo purchase PDF discount report
        Odoo bulk purchase discount
        Odoo procurement negotiation tool
        Odoo purchase order discount approval
        Odoo vendor bill discount automation
        Odoo purchase savings module
        Odoo purchase workflow optimization
        Odoo discount management for procurement
        Odoo supplier deal discounting
        Odoo purchase order discount calculator
        How to apply global discount in Odoo purchase orders
        Odoo module for fixed amount discount in purchase
        Odoo purchase order discount with PDF integration
        Odoo procurement discount tool with access control
        Apply vendor discount automatically in Odoo 19
        Apply vendor discount automatically in Odoo 18
        Apply vendor discount automatically in Odoo 17
        Apply vendor discount automatically in Odoo 16
        Odoo purchase order discount for supplier negotiation
        Discount management in Odoo 19 purchase orders
        Discount management in Odoo 18 purchase orders
        Discount management in Odoo 17 purchase orders
        Discount management in Odoo 16 purchase orders
    """,
    'description': """
            Purchase Order Line Discount
        
            This module enhances the Purchase module by adding discount support at the line level. It adjusts subtotal and tax calculations accordingly.
            
            Key Features:
            - Adds a "Discount (%)" field to Purchase Order Lines
            - Automatically recalculates line subtotals based on discount
            - Discounts are included in tax computations
            - Clean integration with existing purchase workflow
            - Easily extendable for global or tiered discount logic
            - Fully compatible with Odoo 16 Community & Enterprise       
             tus
             techultra
             techultra_private_limited_solution
             Odoo 19 purchase discount
             Odoo 18 purchase discount
             Odoo 17 purchase discount
             Odoo 16 purchase discount
             Odoo purchase global discount
             Odoo vendor discount module        
             Odoo purchase order discount wizard       
             Odoo fixed amount discount
             Odoo percentage discount on purchase        
             Odoo procurement discount management       
             Odoo purchase order PDF discount        
             Odoo supplier discount automation        
             Odoo 19 discount on purchase orders
             Odoo 18 discount on purchase orders
             Odoo 17 discount on purchase orders
             Odoo 16 discount on purchase orders
             Odoo 19 purchase global discount
             Odoo 18 purchase global discount
             Odoo 17 purchase global discount
             Odoo 16 purchase global discount
             Odoo purchase order discount module
             odoo
             odoo16
             odoo17
             odoo18
             odoo19
             Odoo procurement discount management
             Odoo vendor discount automation
             Odoo purchase order fixed discount
             Odoo purchase percentage discount
             Odoo supplier discount tool
             Odoo 19 purchase discount wizard
             Odoo 18 purchase discount wizard
             Odoo 17 purchase discount wizard
             Odoo 16 purchase discount wizard
             Odoo purchase PDF discount report
             Odoo bulk purchase discount
             Odoo procurement negotiation tool
             Odoo purchase order discount approval
             Odoo vendor bill discount automation
             Odoo purchase savings module
             Odoo purchase workflow optimization
             Odoo discount management for procurement
             Odoo supplier deal discounting
             Odoo purchase order discount calculator
             How to apply global discount in Odoo purchase orders
             Odoo module for fixed amount discount in purchase
             Odoo purchase order discount with PDF integration
             Odoo procurement discount tool with access control
             Apply vendor discount automatically in Odoo 19
             Apply vendor discount automatically in Odoo 18
             Apply vendor discount automatically in Odoo 17
             Apply vendor discount automatically in Odoo 16
             Odoo purchase order discount for supplier negotiation
             Discount management in Odoo 19 purchase orders
             Discount management in Odoo 18 purchase orders
             Discount management in Odoo 17 purchase orders
             Discount management in Odoo 16 purchase orders
    """,
    'license': 'OPL-1',
    'price': 0,

    'depends': ['purchase'],
    'data': [
        'security/ir.model.access.csv',
        'security/purchase_discount_security.xml',
        'report/purchase_report_templates.xml',
        'wizard/purchase_order_discount_views.xml',
        'views/purchase_order_view.xml',
        'views/res_config_settings_views.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'installable': True,
    'auto_install': False,

}
