# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Pending Payment Report | Customer & Vendor Outstanding Report',
    'version': '17.0.0.0',
    'category': 'Accounting',
    'summary': """
    Monitor outstanding customer invoices and vendor bills with detailed pending payment reports, helping streamline payment follow-ups and financial tracking.
    Pending Payment Report
    Outstanding Invoice Report
    Vendor Bill Pending Report
    Customer Outstanding Report
    Accounts Receivable Report
    Accounts Payable Report
    Invoice Aging Report
    Pending Invoice Excel Report
    Outstanding Payment Tracking
    Invoice Due Report
    Vendor Outstanding Balance
    Customer Payment Follow-up
    Financial Reporting Module
    Invoice Status Report
    Bill Payment Tracking
    Accounting Excel Report
    Pending Payment PDF Report
    Multi-Currency Invoice Report
    Grand Total Financial Report
    Invoice Balance Summary
    Vendor Due Amount Report
    Customer Due Summary
    Receivable Management Tool
    Payable Management System
    Outstanding Balance Excel Export
    Invoice Payment Summary
    Advanced Accounting Report
    Automatic Payment Reminder
    Invoice Grouped by Customer
    Vendor Bill Grouped Report
    Payment Follow-up Automation
    Pending Amount Tracking
    Invoice Payment Analytics
    Financial Due Report
    Outstanding Tracking System
    Accounting Report Export
    Customer Ledger Pending
    Vendor Ledger Outstanding
    Smart Pending Invoice Manager
    Invoice Due Date Tracking
    Accounts Due Monitoring
    Business Payment Tracking
    Invoice & Bill Outstanding Report
    Payment Status Summary
    odoo18
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'description': """
    Pending Payment Report | Customer & Vendor Outstanding Invoice Report is a comprehensive Odoo accounting solution designed to help businesses efficiently monitor and manage outstanding customer invoices and vendor bills. The module provides detailed visibility into pending receivables and payables, enabling organizations to improve cash flow management and streamline payment follow-up processes.
    Pending Payment Report
    Outstanding Invoice Report
    Vendor Bill Pending Report
    Customer Outstanding Report
    Accounts Receivable Report
    Accounts Payable Report
    Invoice Aging Report
    Pending Invoice Excel Report
    Outstanding Payment Tracking
    Invoice Due Report
    Vendor Outstanding Balance
    Customer Payment Follow-up
    Financial Reporting Module
    Invoice Status Report
    Bill Payment Tracking
    Accounting Excel Report
    Pending Payment PDF Report
    Multi-Currency Invoice Report
    Grand Total Financial Report
    Invoice Balance Summary
    Vendor Due Amount Report
    Customer Due Summary
    Receivable Management Tool
    Payable Management System
    Outstanding Balance Excel Export
    Invoice Payment Summary
    Advanced Accounting Report
    Automatic Payment Reminder
    Invoice Grouped by Customer
    Vendor Bill Grouped Report
    Payment Follow-up Automation
    Pending Amount Tracking
    Invoice Payment Analytics
    Financial Due Report
    Outstanding Tracking System
    Accounting Report Export
    Customer Ledger Pending
    Vendor Ledger Outstanding
    Smart Pending Invoice Manager
    Invoice Due Date Tracking
    Accounts Due Monitoring
    Business Payment Tracking
    Invoice & Bill Outstanding Report
    Payment Status Summary
    odoo18
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com/',
    'depends': ["account", "mail"],
    'data': [
        "security/ir.model.access.csv",
        "data/mail_template.xml",
        "report/pending_payment_report_templates.xml",
        "report/pending_payment_report.xml",
        "report/advance_pending_payment_report_templates.xml",
        "report/advance_pending_payment_report.xml",
        "views/res_config_settings_views.xml",
        "views/pending_payment_report_views.xml",
        "views/advance_pending_payment_report_views.xml",
        "views/menu.xml",
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 22.99,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    "application": False,
}
