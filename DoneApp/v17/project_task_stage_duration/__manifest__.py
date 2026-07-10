# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': 'Task Stage History & Duration Management | Project Process Tracking | Odoo Project Analytics',
    'version': '17.0.0.0',
    'category': 'Services/Project',
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com/',
    'summary': """Track task stage duration, time in stage, workflow history and stage templates 
    
        tus
        techultra
        techultra_private_limited_solution
        project task
        project
        tracker
        state
        stage track
        task
        global project task track
        project task stage tracker
        task stage duration tracker
        project workflow tracker
        task workflow history
        stage transition tracker
        project stage analytics
        task lifecycle tracking
        project workflow analytics
        stage duration monitoring
        workflow performance tracker
        task stage history logger
        project stage change history
        task movement tracking
        stage transition history
        workflow stage time tracking
        project task duration tracker
        stage performance analysis
        workflow bottleneck detection
        project task analytics
        task stage monitoring
        project workflow optimization
        project performance monitoring
        task progress tracking
        workflow efficiency analytics
        project timeline analysis
        task management analytics
        stage productivity tracking
        project process tracking
        team workflow analysis
        task lifecycle analytics
        automated stage tracking
        task stage change log
        project stage audit trail
        workflow stage logging
        stage time calculation
        task workflow automation
        stage duration report
        project task history tracking
        workflow stage metrics
        project workflow insights
        workflow bottleneck analysis
        stage time reporting
        project stage metrics
        task workflow monitoring
        workflow timeline tracker
        project task transition log
        task movement analytics
        project lifecycle insights
        task stage performance tracker
        workflow history tracker
        project stage duration report
        team workflow productivity tracker
        project stage audit logger
        task stage duration analytics
        project audit trail tracker
        task stage audit log
        workflow history audit
        project activity history tracker
        workflow change history
        task activity monitoring
        project workflow audit system
        stage change audit log
        project movement tracking
        task history monitoring tool
        team productivity tracking
        workflow bottleneck tracker
        project efficiency analysis
        team workflow optimization
        productivity analytics for projects
        task efficiency tracking
        workflow performance improvement
        project workflow optimization tool
        team task progress monitoring
        workflow process improvement
        automated workflow tracking
        automated task stage monitoring
        smart workflow analytics
        intelligent stage tracking
        automated stage history logging
        workflow automation analytics
        task lifecycle automation tracking
        stage automation reporting
        automated project tracking
        intelligent workflow monitoring
                
            
    """,
    'description': """
Project Task Stage Duration & History | Odoo 17
================================================
Track how long project tasks stay in each stage and keep full workflow history.

• Task stage duration tracking – Record time spent in each task stage (Stage In, Stage Out, Duration).
• Task stage history – View per-task stage progression and full stage transition log.
• Task Stage Lifetime report – List all stage changes with filters and group by Stage, Task, or Project.
• Stage History view – From Stage, To Stage, Start, Stop, Duration, User, Project, Task.
• Global and per-project settings – Enable or disable tracking (START/STOP) for all projects or by project.
• Project stage flags – Mark stages as Project Stage with Start/Stop for duration control.
• Stage templates – Reusable stage pipelines (e.g. New, In Progress, Done) with tracking options.
• Mass update stages – Change task stage from list view; every change is recorded in history.

Ideal for: project task time tracking, workflow analysis, bottleneck detection, stage duration reports, and Odoo project management.

        tus
        techultra
        techultra_private_limited_solution
        project task
        project
        tracker
        state
        stage track
        task
        global project task track
        project task stage tracker
        task stage duration tracker
        project workflow tracker
        task workflow history
        stage transition tracker
        project stage analytics
        task lifecycle tracking
        project workflow analytics
        stage duration monitoring
        workflow performance tracker
        task stage history logger
        project stage change history
        task movement tracking
        stage transition history
        workflow stage time tracking
        project task duration tracker
        stage performance analysis
        workflow bottleneck detection
        project task analytics
        task stage monitoring
        project workflow optimization
        project performance monitoring
        task progress tracking
        workflow efficiency analytics
        project timeline analysis
        task management analytics
        stage productivity tracking
        project process tracking
        team workflow analysis
        task lifecycle analytics
        automated stage tracking
        task stage change log
        project stage audit trail
        workflow stage logging
        stage time calculation
        task workflow automation
        stage duration report
        project task history tracking
        workflow stage metrics
        project workflow insights
        workflow bottleneck analysis
        stage time reporting
        project stage metrics
        task workflow monitoring
        workflow timeline tracker
        project task transition log
        task movement analytics
        project lifecycle insights
        task stage performance tracker
        workflow history tracker
        project stage duration report
        team workflow productivity tracker
        project stage audit logger
        task stage duration analytics
        project audit trail tracker
        task stage audit log
        workflow history audit
        project activity history tracker
        workflow change history
        task activity monitoring
        project workflow audit system
        stage change audit log
        project movement tracking
        task history monitoring tool
        team productivity tracking
        workflow bottleneck tracker
        project efficiency analysis
        team workflow optimization
        productivity analytics for projects
        task efficiency tracking
        workflow performance improvement
        project workflow optimization tool
        team task progress monitoring
        workflow process improvement
        automated workflow tracking
        automated task stage monitoring
        smart workflow analytics
        intelligent stage tracking
        automated stage history logging
        workflow automation analytics
        task lifecycle automation tracking
        stage automation reporting
        automated project tracking
        intelligent workflow monitoring
    """,
    'depends': ['project'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_task_type_views.xml',
        'views/project_project_views.xml',
        'views/project_task_views.xml',
        'views/project_task_stage_history_views.xml',
        'views/project_stage_template_views.xml',
        'views/res_config_settings_views.xml',
        'views/project_menus.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'currency': 'USD',
    'price': 16.00,
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}
