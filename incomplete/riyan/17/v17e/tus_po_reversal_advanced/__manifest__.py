# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    "name": "Purchase Cancel / Reverse / Reset (Advanced)",
    "summary": """Cancel, reverse and reset POs, pickings and vendor bills with audit & policies
    
    tus
    techultra
    techultra_private_limited_solution
    purchase 
    purchase cancel
    purchase reverse
    purchase reset
    purchase advanced
    po reverse odoo
    odoo reset picking
    reset vendor bill
    cancel purchase order odoo
    reverse vendor bill
    return picking odoo
    reset to draft odoo
    advanced cancellation
    undo purchase order
    cancel stock transfer
    reverse stock move
    multi company purchase
    accounting reversal odoo
    refund bill odoo
    undo vendor bill
    workflow correction
    po cancel and reverse
    Purchase Management
    Inventory / Stock
    Accounting
    Productivity Tools
    Workflow Automation
    Multi-company Management
    Odoo purchase cancel module
    Odoo reverse purchase order
    Odoo PO reset to draft
    Odoo vendor bill reversal
    cancel purchase order Odoo
    reverse vendor bill Odoo
    reset picking to draft Odoo
    Odoo reverse stock picking
    Odoo cancel receipt
    Odoo advanced cancellation
    Odoo undo purchase order
    Odoo PO cancellation workflow
    purchase order reversal Odoo
    Odoo return picking automation
    Odoo cancel vendor bill
    Odoo refund vendor bill
    Odoo reverse stock transfer
    stock picking reset Odoo
    multi company cancel module Odoo
    Odoo cancel validated PO
    how to cancel a validated purchase order in Odoo
    cancel PO with receipts in Odoo
    reverse posted vendor bill Odoo
    reset posted vendor bill to draft Odoo
    cancel purchase workflow Odoo
    reverse picking with valuation Odoo
    Odoo purchase order reversal tool
    cancel PO with dependencies Odoo
    Odoo return picking creation
    cancel and reverse purchase receipts Odoo
    Odoo workflow reset module
    Odoo reversal automation
    Odoo purchase management extension
    Odoo cancellation API
    undo stock move Odoo
    reset invoice Odoo
    Odoo stock workflow override
    Odoo accounting reversal customization
    Odoo purchase corrections
    Odoo cancellation utilities
    Odoo audit-friendly cancellation
    Odoo multi-company cancellation
    Odoo advanced purchase management
    Odoo error correction module
        
    """,
    'description': """
        This module provides advanced cancellation, reversal, and reset-to-draft capabilities for Purchase Orders, Stock Pickings, and Vendor Bills. 
        It allows users to safely correct mistakes in the purchasing workflow while maintaining full auditability and data integrity.
    tus
    techultra
    techultra_private_limited_solution
    purchase 
    purchase cancel
    purchase reverse
    purchase reset
    purchase advanced
    po reverse odoo
    odoo reset picking
    reset vendor bill
    cancel purchase order odoo
    reverse vendor bill
    return picking odoo
    reset to draft odoo
    advanced cancellation
    undo purchase order
    cancel stock transfer
    reverse stock move
    multi company purchase
    accounting reversal odoo
    refund bill odoo
    undo vendor bill
    workflow correction
    po cancel and reverse
    Purchase Management
    Inventory / Stock
    Accounting
    Productivity Tools
    Workflow Automation
    Multi-company Management
    Odoo purchase cancel module
    Odoo reverse purchase order
    Odoo PO reset to draft
    Odoo vendor bill reversal
    cancel purchase order Odoo
    reverse vendor bill Odoo
    reset picking to draft Odoo
    Odoo reverse stock picking
    Odoo cancel receipt
    Odoo advanced cancellation
    Odoo undo purchase order
    Odoo PO cancellation workflow
    purchase order reversal Odoo
    Odoo return picking automation
    Odoo cancel vendor bill
    Odoo refund vendor bill
    Odoo reverse stock transfer
    stock picking reset Odoo
    multi company cancel module Odoo
    Odoo cancel validated PO
    how to cancel a validated purchase order in Odoo
    cancel PO with receipts in Odoo
    reverse posted vendor bill Odoo
    reset posted vendor bill to draft Odoo
    cancel purchase workflow Odoo
    reverse picking with valuation Odoo
    Odoo purchase order reversal tool
    cancel PO with dependencies Odoo
    Odoo return picking creation
    cancel and reverse purchase receipts Odoo
    Odoo workflow reset module
    Odoo reversal automation
    Odoo purchase management extension
    Odoo cancellation API
    undo stock move Odoo
    reset invoice Odoo
    Odoo stock workflow override
    Odoo accounting reversal customization
    Odoo purchase corrections
    Odoo cancellation utilities
    Odoo audit-friendly cancellation
    Odoo multi-company cancellation
    Odoo advanced purchase management
    Odoo error correction module   
    
    
    """,
    "version": "17.0.0.0",
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    "category": "Purchases",
    "depends": ["purchase_stock", "account"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/res_config_settings_data.xml",
        "data/server_actions.xml",
        "views/res_config_settings_views.xml",
        "views/audit_log_views.xml",
        "views/purchase_order_views.xml",
        "views/stock_picking_views.xml",
        "views/account_move_views.xml",
        "views/wizard_views.xml",
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'currency': 'USD',
    'price': 25.00,
    "license": "OPL-1",
    "installable": True,
    "application": True,
    "auto_install": False,
}
