# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    "name": "Pricelist User Access Control | Centralized Pricelist Control | User-Specific Pricelist Access",
    "version": "17.0.0.0",
    "category": "Sales",
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    "summary": """
    Custom Pricelist Access for Sales Orders helps businesses control user access to pricelists within the Odoo Sales workflow. Administrators can assign authorized pricelists to specific users, preventing unauthorized pricing changes and improving quotation accuracy, pricing security, and sales management efficiency.
    Pricelist Access Control
    User-Based Pricelist Management
    Sales Pricelist Restrictions
    Secure Pricing Access
    Sales Pricing Security
    User Pricelist Permissions
    Restricted Pricelist Selection
    Sales Order Pricing Control
    Advanced Pricelist Security
    Role-Based Pricing Access
    Sales Pricing Governance
    Pricelist Permission Manager
    Controlled Pricing Workflow
    Secure Sales Pricing
    Multi-User Pricelist Control
    Dynamic Pricing Restrictions
    Quotation Pricing Security
    Authorized Pricelist Access
    Pricing Rule Enforcement
    Business Pricing Control
    Sales Team Pricing Access
    Intelligent Pricelist Management
    User-Specific Pricing Rules
    Customer Pricing Restrictions
    Wholesale Pricing Access
    Regional Pricing Management
    Enterprise Pricing Security
    Secure Quotation Management
    Odoo Pricelist Access Control
    Odoo Sales Pricing Security
    """,
    "description": """
    Custom Pricelist Access for Sales Orders is an advanced Odoo security module that allows administrators to assign and restrict pricelists for individual users in the Sales module. Users can only access authorized pricelists while creating quotations and sales orders, preventing incorrect pricing and unauthorized changes. This helps businesses maintain pricing accuracy, improve sales control, and reduce pricing errors across teams, branches, and departments. The module integrates seamlessly with the standard Odoo Sales workflow.
    Pricelist Access Control
    User-Based Pricelist Management
    Sales Pricelist Restrictions
    Secure Pricing Access
    Sales Pricing Security
    User Pricelist Permissions
    Restricted Pricelist Selection
    Sales Order Pricing Control
    Advanced Pricelist Security
    Role-Based Pricing Access
    Sales Pricing Governance
    Pricelist Permission Manager
    Controlled Pricing Workflow
    Secure Sales Pricing
    Multi-User Pricelist Control
    Dynamic Pricing Restrictions
    Quotation Pricing Security
    Authorized Pricelist Access
    Pricing Rule Enforcement
    Business Pricing Control
    Sales Team Pricing Access
    Intelligent Pricelist Management
    User-Specific Pricing Rules
    Customer Pricing Restrictions
    Wholesale Pricing Access
    Regional Pricing Management
    Enterprise Pricing Security
    Secure Quotation Management
    Odoo Pricelist Access Control
    Odoo Sales Pricing Security
    """,
    "depends": ["product", "sale_management"],
    'data': [
        'security/pricelist_restriction_rule.xml',
        'views/product_pricelist_view.xml',
    ],
    'images': [
        'static/description/main_screen.gif'
    ],
    'price': 13.86,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
