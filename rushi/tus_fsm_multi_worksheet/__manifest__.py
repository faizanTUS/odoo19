# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Field Service Multi Worksheet',
    'version': '19.0',
    'category': 'Services/Field Service',
    'summary': """Field Service Management Multi Worksheet""",
    'description': """Able to add multi-worksheet in field service and print in task report
        Field
        Service
        Field Service
        Odoo
        ERP
        Customize
        Multiple Worksheet
        Worksheet
        Sheet
        FSM
        Odoo Erp
        Fields Service Worksheet
        Task Report
        """,
    'author': "Techultra Solutions Private Limited",
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'depends': ['project', 'industry_fsm','industry_fsm_report','product'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_task_view.xml',
        'report/worksheet_custom_report.xml',
    ],
    'images': [
        'static/description/tus_banner.gif',
    ],
    'currency': 'USD',
    'price': 16,
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
}
