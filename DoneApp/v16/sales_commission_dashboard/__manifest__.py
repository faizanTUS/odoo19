# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': "Sales Commission Dashboard | Sales Team Performance, Quotations, Deliveries & Invoice Insights",
    'author': 'TechUltra Solutions Private Limited',
    'category': 'Sales/Sales',
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com',
    'version': '16.0.0.0',
    'summary': """
    Track sales activities, customer follow-ups, invoice due dates, and commission performance from a single Odoo dashboard with real-time insights and a modern UI.
    Odoo Sales Commission Dashboard
    Odoo Sales Dashboard
    Sales Commission Dashboard Odoo
    Odoo Commission Summary
    Odoo Salesperson Performance Dashboard
    Odoo Sales Target Dashboard
    Odoo Sales Reporting Dashboard
    Odoo Sales Team Dashboard
    Odoo Quotation Dashboard
    Odoo Pending Sales Order Dashboard
    Odoo Delivery Dashboard
    Odoo Pending Deliveries
    Odoo Invoice Due Date Dashboard
    Odoo Customer Activity Dashboard
    Odoo Inactive Customers
    Odoo Sales Performance Tracking
    Odoo User Wise Sales Report
    Odoo Sales Manager Dashboard
    Sales commission dashboard for Odoo 18
    Odoo dashboard for sales team performance
    Odoo module to track sales commission
    Odoo sales dashboard with pending quotations
    Odoo dashboard for pending deliveries and invoices
    Odoo sales user performance tracking module
    Odoo commission summary for salespersons
    Odoo invoice payment due date dashboard
    Odoo inactive customer tracking dashboard
    Best Odoo sales dashboard module
    """,
    'description': """
    Sales Commission Dashboard is a modern Odoo dashboard module that helps businesses track quotations, deliveries, invoice due dates, inactive customers, and salesperson performance from one centralized view. It also includes a Commission Summary Dashboard to monitor sales targets and commission achievements in real time.
    Odoo Sales Commission Dashboard
    Odoo Sales Dashboard
    Sales Commission Dashboard Odoo
    Odoo Commission Summary
    Odoo Salesperson Performance Dashboard
    Odoo Sales Target Dashboard
    Odoo Sales Reporting Dashboard
    Odoo Sales Team Dashboard
    Odoo Quotation Dashboard
    Odoo Pending Sales Order Dashboard
    Odoo Delivery Dashboard
    Odoo Pending Deliveries
    Odoo Invoice Due Date Dashboard
    Odoo Customer Activity Dashboard
    Odoo Inactive Customers
    Odoo Sales Performance Tracking
    Odoo User Wise Sales Report
    Odoo Sales Manager Dashboard
    Sales commission dashboard for Odoo 18
    Odoo dashboard for sales team performance
    Odoo module to track sales commission
    Odoo sales dashboard with pending quotations
    Odoo dashboard for pending deliveries and invoices
    Odoo sales user performance tracking module
    Odoo commission summary for salespersons
    Odoo invoice payment due date dashboard
    Odoo inactive customer tracking dashboard
    Best Odoo sales dashboard module
    """,
    'license': 'OPL-1',
    'depends': ['base', 'sale', 'sales_team', 'stock', 'account', 'sale_commission'],
    'data': [
        'views/sales_commission_dashboard_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sales_commission_dashboard/static/src/css/sales_commission_dashboard.css',
            'sales_commission_dashboard/static/src/xml/sales_commission_dashboard.xml',
            'sales_commission_dashboard/static/src/js/sales_commission_dashboard.js',
        ],
    },
    'images': ['static/description/main_screen.gif'],
    'price': 23.30,
    'currency': 'USD',
    'application': True,
    'installable': True,
    'auto_install': False,
}
