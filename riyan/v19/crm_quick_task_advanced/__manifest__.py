# -*- coding: utf-8 -*-
{
    'name': 'Quick Task from Leads/Opportunity (Advanced)',
    'version': '19.0.1.0',
    'category': 'Customer Relationship Management',
    'summary': 'Create project tasks directly from Leads or Opportunities with pre-filled data',
    'description': """
Quick Task from Leads/Opportunity (Advanced)
============================================
* Add a **Task** tab on Lead/Opportunity form with a **Quick Task** button.
* Create tasks with Subject, Project, Tags, Assignee and Customer pre-filled from the lead/opportunity.
* Configure default project per Sales Team (or use company default).
* Link created tasks back to the source Lead/Opportunity for traceability.
    """,
    'author': 'Odoo Community',
    'website': 'https://www.odoo.com/community',
    'license': 'LGPL-3',
    'depends': ['crm', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_team_views.xml',
        'views/crm_lead_views.xml',
        'views/project_task_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
