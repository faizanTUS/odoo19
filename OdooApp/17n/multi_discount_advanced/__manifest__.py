# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
{
    'name': 'Advanced Multi Discount for Sales, Purchase & Accounting',
    'version': '17.0.0.0',
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'category': 'Sales/Purchase/Accounting',
    'summary': """Advanced Multi Discount for Sales, Purchase & Accounting - Apply multiple discounts on sales, purchase orders, and acounting
        Easily apply multiple discounts (Scheme Discount, Cash Discount, Special Discount) on sales orders, purchase orders, and accounting. Display multi-discount in PDF reports with full control.
        
        tus
        TUS
        TechUltra Solutions Private Limited
        techUltra solutions private limited
        multi discount
        multiple discount
        fixed multi discount
        Advanced Multi Discount for Sales, Purchase & Accounting
        Advanced Multi Discount for Sales
        Advanced Multi Discount for Accounting
        Advanced Multi Discount for Purchase
        fixed discount
        multi discount on sales
        multi discount on purchase
        multi discount on invoice
        fixed discount before percentage discount
        line level multi discount
        line discount
        line level discount
        multi level discount
        discount calculation
        sequential discount
        discount before tax
        sales discount
        sale order discount
        quotation discount
        purchase discount
        purchase order discount
        rfq discount
        invoice discount
        customer invoice discount
        vendor bill discount
        accounting discount
        discount management
        pricing discount
        pricing calculation
        tax after discount
        discount on order lines
        discount on invoice lines
        user based discount
        discount permission
        advanced discount
        line level discount
        sequential discount
        fixed amount discount
        percentage discount
        sales discount
        purchase discount
        invoice discount
        accounting discount
        multi level discount
        discount calculation
        pricing management
        discount before tax
        scheme discount
        cash discount
        special discount
        odoo multi discount
        odoo multi discount module
        sales discount
        purchase discount
        invoice discount
        vendor bill discount
        PDF discount report
        multi discount advanced
        advanced discount
        fixed discount
        line discount
        sales discount
        purchase discount
        invoice discount
        accounting discount
        multi level discount
        discount calculation
        discount management
        fixed amount discount
        percentage discount
        discount before tax
        pricing discount
        sale order discount
        purchase order discount
        customer invoice discount
        vendor bill discount
        discount on lines
        fixed and percentage discount
        sales purchase invoice discount
        enterprise discount management
        pricing accuracy
        Advanced Multi Discount - Fixed & Percentage Discount Calculation
        fixed multi discount on sales orders
        multi discount on purchase orders
        invoice multi discount calculation
        fixed discount before percentage discount
        sequential discount calculation
        line level discount management
        advanced discount management
        accurate discount and tax calculation
        multi discount on pdf report
        user based discount access
        discount management
        odoo discount module
    """,
    'description': """
Advanced Multi Discount – Fixed & Percentage Discount Calculation Module
==============================

This module extends Odoo's discount functionality by allowing you to apply multiple discounts on sales orders, purchase orders, and accounting.

Key Features:
-------------
* Multi Discount Field: Add a fixed amount discount (Multi Discount) on each order/invoice line
* User Configuration: Enable/disable multi-discount feature per user for Sales, Purchase, and Accounting
* PDF Reports: Option to show/hide multi-discount column in PDF reports
* Automatic Calculations: Multi-discount is applied before percentage discount, ensuring accurate pricing
* Full Integration: Works seamlessly with existing discount and tax calculations

Supported Documents:
-------------------
* Sales Orders (Quotations)
* Purchase Orders (RFQ)
* Accounting


Configuration:
--------------
1. Go to Settings > Users & Companies > Users
2. Select a user and enable:
   - Multi Discount on Sale
   - Multi Discount on Purchase
   - Multi Discount on Account

Usage:
------
1. Create a Sales Order, Purchase Order, and Accounting
2. Add products to order lines
3. Enter the Multi Discount amount in the "Multi Discount" field
4. The system automatically calculates:
   - Discounted Total Amount (after multi-discount)
   - Discount Percentage (based on multi-discount)
   - Final subtotal with taxes

PDF Reports:
------------
* Check "Show Multi Discount in PDF Report" checkbox to display multi-discount column
* Multi-discount appears in Quotation, Sales Order, RFQ, Purchase Order, and Accounting PDFs

Technical Details:
------------------
* Multi-discount is a fixed monetary amount deducted from the unit price
* Percentage discount is then applied on the discounted price
* All calculations respect tax configurations
* Compatible with Odoo Community and Enterprise editions
        
        
        tus
        TUS
        TechUltra Solutions Private Limited
        techUltra solutions private limited
        multi discount
        multiple discount
        fixed multi discount
        fixed discount
        multi discount on sales
        multi discount on purchase
        multi discount on invoice
        Advanced Multi Discount for Sales, Purchase & Accounting
        Advanced Multi Discount for Sales
        Advanced Multi Discount for Accounting
        Advanced Multi Discount for Purchase
        fixed discount before percentage discount
        line level multi discount
        line discount
        line level discount
        multi level discount
        discount calculation
        sequential discount
        discount before tax
        sales discount
        sale order discount
        quotation discount
        purchase discount
        purchase order discount
        rfq discount
        invoice discount
        customer invoice discount
        vendor bill discount
        accounting discount
        discount management
        pricing discount
        pricing calculation
        tax after discount
        discount on order lines
        discount on invoice lines
        user based discount
        discount permission
        advanced discount
        line level discount
        sequential discount
        fixed amount discount
        percentage discount
        sales discount
        purchase discount
        invoice discount
        accounting discount
        multi level discount
        discount calculation
        pricing management
        discount before tax
        scheme discount
        cash discount
        special discount
        odoo multi discount
        odoo multi discount module
        sales discount
        purchase discount
        invoice discount
        vendor bill discount
        PDF discount report
        multi discount advanced
        advanced discount
        fixed discount
        line discount
        sales discount
        purchase discount
        invoice discount
        accounting discount
        multi level discount
        discount calculation
        discount management
        fixed amount discount
        percentage discount
        discount before tax
        pricing discount
        sale order discount
        purchase order discount
        customer invoice discount
        vendor bill discount
        discount on lines
        fixed and percentage discount
        sales purchase invoice discount
        enterprise discount management
        pricing accuracy
        Advanced Multi Discount - Fixed & Percentage Discount Calculation
        fixed multi discount on sales orders
        multi discount on purchase orders
        invoice multi discount calculation
        fixed discount before percentage discount
        sequential discount calculation
        line level discount management
        advanced discount management
        accurate discount and tax calculation
        multi discount on pdf report
        user based discount access
        discount management
        odoo discount module
    """,
    'depends': ['sale', 'purchase', 'account'],
    'data': [
        'security/security_group.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/account_move_views.xml',
        'report/sale_report_templates.xml',
        'report/purchase_report_templates.xml',
        'report/account_invoice_report_templates.xml',
    ],
    'images': [
        'static/description/main_screen.gif'
    ],
    'price': 24.90,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}

