# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
{
    "name": "Petty Cash Dashboard & Expense Manager | Petty Cash Fund, Voucher & Expense Management System | Petty Cash Financial Control & Insights",
    "version": "17.0.0.0",
    "category": "Accounting",
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    "summary": """
    Manage multiple petty cash funds with tiered approval workflows, expense policies, and seamless GL integration. This module provides real-time dashboard analytics and automated replenishment requests to ensure efficient and transparent cash handling.
    cash fund management
    cash balance tracking
    fund monitoring system
    cash reconciliation
    financial tracking system
    expense control system
    cash flow tracking
    financial management tool
    expense tracking
    expense management system
    expense voucher management
    voucher tracking system
    expense approval workflow
    expense recording system
    receipt tracking system
    expense control software
    cash replenishment
    fund replenishment system
    cash refill process
    approval workflow system
    request approval system
    financial workflow automation
    financial dashboard
    expense dashboard
    kpi dashboard
    analytics dashboard
    financial reporting
    expense reporting
    business insights dashboard
    real-time reporting system    
     """,

    "description": """
    This module offers a comprehensive solution for managing small-cash spending with professional accounting rigor. It features configurable approval matrices, spend limit policies, and full voucher lifecycle tracking from draft to posted entry. The module includes critical balance alerts, aging analysis reports, and multi-company support, making it ideal for organizations seeking audit-ready financial compliance and streamlined internal controls.
    cash fund management
    cash balance tracking
    fund monitoring system
    cash reconciliation
    financial tracking system
    expense control system
    cash flow tracking
    financial management tool
    expense tracking
    expense management system
    expense voucher management
    voucher tracking system
    expense approval workflow
    expense recording system
    receipt tracking system
    expense control software
    cash replenishment
    fund replenishment system
    cash refill process
    approval workflow system
    request approval system
    financial workflow automation
    financial dashboard
    expense dashboard
    kpi dashboard
    analytics dashboard
    financial reporting
    expense reporting
    business insights dashboard
    real-time reporting system
    """,
    "depends": ["account", "mail", "hr", "web", "web_editor"],
    "data": [
        "security/petty_cash_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/petty_cash_cron.xml",
        "data/ir_actions_server.xml",
        "views/petty_cash_category_views.xml",
        "views/petty_cash_policy_views.xml",
        "views/petty_cash_approval_rule_views.xml",
        "views/petty_cash_fund_views.xml",
        "views/petty_cash_voucher_views.xml",
        "views/petty_cash_replenishment_views.xml",
        "views/account_move_views.xml",
        "views/petty_cash_menus.xml",
        "wizard/petty_cash_approval_reject_views.xml",
        "report/petty_cash_aging_report.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "petty_cash_management/static/src/scss/petty_cash_dashboard.scss",
            "petty_cash_management/static/src/js/petty_cash_dashboard.js",
            "petty_cash_management/static/src/xml/petty_cash_dashboard.xml",
        ],
    },
    "demo": [
        "data/petty_cash_demo.xml",
    ],
    'images': [
        'static/description/main_screen.gif'
    ],
    'price': 39.95,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    "post_init_hook": "post_init_hook",
}
