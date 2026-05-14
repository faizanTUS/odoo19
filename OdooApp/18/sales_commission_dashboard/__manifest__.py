# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': 'Sales Commission Dashboard',
    'version': '18.0.0.0.0',
    'category': 'Sales/Sales',
    'sequence': 15,
    'summary': 'Sales activity and commission dashboard with per-user filters.',
    'description': """
Sales Commission Dashboard
==========================

Track pending quotations, overdue invoices, outgoing deliveries that are still
not done, and customers with no recent sales orders. Filter the dashboard by
internal sales user.

When ``sale_commission`` is installed, the commission summary uses
``sale.commission.report`` (targets, achievement, commission).

Keywords: sales dashboard, commission, quotations, deliveries, invoices,
inactive customers, salesperson filter.
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
        'sale_commission',
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
    'odoo_version': '18.0',
}
