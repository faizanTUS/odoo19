# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': 'Sales Commission Dashboard',
    'version': '17.0.0.0.0',
    'category': 'Sales/Sales',
    'sequence': 15,
    'summary': 'Sales activity dashboard with per-user filters.',
    'description': """
Sales Commission Dashboard
==========================

Track pending quotations, overdue invoices, outgoing deliveries that are still
not done, and customers with no recent sales orders. Filter the dashboard by
internal sales user.

The commission summary table is reserved for editions that ship the
``sale_commission`` module (for example Odoo 18+ with that app installed). This
build focuses on quotations, deliveries, invoices, and inactive customers.

Keywords: sales dashboard, quotations, deliveries, invoices, inactive customers,
salesperson filter.
    """,
    'author': 'Techultra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com/',
    'license': 'OPL-1',
    'depends': [
        'base',
        'sale',
        'sales_team',
        'stock',
        'account',
    ],
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
    'application': False,
    'installable': True,
    'auto_install': False,
    'price': 12,
    'currency': 'EUR',
    'odoo_version': '17.0',
}
