# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Purchase Global Discount Advanced | Apply Percentage, Fixed & Global Discounts on Purchase Orders in Odoo',
    'version': '19.0.0.0',
    'author': 'Techultra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'category': 'Purchase',
    'summary': """Purchase Global Discount Advanced | Apply Percentage, Fixed & Global Discounts on Purchase Orders in Odoo 
                Easily apply percentage, global, or fixed amount discounts on purchase orders. This module automates discount calculation, integrates with vendor bills and reports, and includes role-based access control for secure and efficient procurement management.
                tus
                techultra
                techultra_private_limited_solution
                purchase discount Odoo
    Odoo purchase global discount
    Odoo purchase order discount
    purchase fixed discount Odoo
    Odoo vendor bill discount
    Odoo purchase discount module
    Odoo global discount purchase order
    purchase order percentage discount Odoo
    Odoo supplier discount
    Odoo purchase management discount
    Odoo discount wizard
    Odoo purchase advanced discount
    vendor bill global discount Odoo
    Odoo purchase order fixed amount discount
    Odoo purchase subtotal discount
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
                - Fully compatible with Odoo 17 Community & Enterprise        

                tus
                techultra
                techultra_private_limited_solution
                purchase discount Odoo
    Odoo purchase global discount
    Odoo purchase order discount
    purchase fixed discount Odoo
    Odoo vendor bill discount
    Odoo purchase discount module
    Odoo global discount purchase order
    purchase order percentage discount Odoo
    Odoo supplier discount
    Odoo purchase management discount
    Odoo discount wizard
    Odoo purchase advanced discount
    vendor bill global discount Odoo
    Odoo purchase order fixed amount discount
    Odoo purchase subtotal discount
        """,
    'license': 'OPL-1',
    'price': 20,
    'currency': 'EUR',
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
