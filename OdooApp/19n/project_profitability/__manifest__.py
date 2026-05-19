# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
{
    'name': 'Project Profitability & Margin Tracking for Odoo',
    'version': '19.0.0.0',
    'category': 'Project',
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'summary': """Custom profitability calculations and tracking for projects
    
        tus
        TUS
        TechUltra Solutions Private Limited
        techUltra solutions private limited
        project
        lead
        dashboard
        kpi
        project overview
        opportunity
        budget
        analytic
        odoo profitability module
        odoo project profitability
        odoo margin tracking
        odoo cost tracking module
        odoo profit analysis
        odoo project margin
        odoo crm profitability
        odoo financial tracking
        odoo profit management
        odoo cost control
        project profitability tracking
        margin analysis software odoo
        profit margin tracking system
        business profitability tools
        project margin analysis
        profit optimization software
        margin control system
        profit tracking software
        gross margin tracking
        net profit analysis
        project cost tracking odoo
        project financial management
        project budget tracking
        project revenue tracking
        cost vs revenue analysis
        project expense tracking
        project performance metrics
        project financial dashboard
        project cost control system
        project accounting insights
        crm profit tracking
        lead profitability analysis
        sales margin tracking
        crm cost analysis
        deal profitability tracking
        sales performance profitability
        revenue vs cost crm
        crm financial insights
        opportunity profit analysis
        sales cost control
        odoo dashboard kpi
        profitability dashboard odoo
        financial dashboard odoo
        kpi tracking system
        business performance dashboard
        margin dashboard
        cost analysis dashboard
        revenue analytics odoo
        financial reporting dashboard
        real time profit tracking
        profitability alerts
        cost overrun alerts
        margin warning system
        automated financial alerts
        project risk alerts
        budget overrun notification
        financial monitoring system
        profit risk management
        automated cost tracking
        smart financial alerts
        odoo crm project integration
        odoo project module extension
        odoo business intelligence
        odoo financial analytics
        odoo custom dashboard
        odoo automation module
        odoo reporting tools
        odoo enterprise addon
        odoo community module
        odoo workflow automation
        agency profitability tracking
        consulting profit management
        service business profitability
        it project cost tracking
        software project margin
        professional services analytics
        resource cost tracking
        time and cost management
        project based business tools
        service margin optimization
        track project profitability in odoo
        how to measure project margin odoo
        odoo module for cost and revenue tracking
        best odoo profitability module
        odoo solution for project cost control
        crm to project profitability tracking
        odoo tool for margin analysis
        project profit dashboard odoo
        odoo app for financial performance
        profit tracking from lead to project
    """,
    'description': """
        Project Profitability & Margin Tracking for Odoo
        =====================
        * Track project revenue, costs, and margins
        * Budget vs actual variance analysis (install account_budget for full support)
        * Profitability status and budget alerts
        * Dashboard with KPIs and trends
        * Excel export and scheduled calculations
        * Demo data: Lead → Opportunity → SO → Project → Budget flow
        
        
        
        tus
        TUS
        TechUltra Solutions Private Limited
        techUltra solutions private limited
        project
        lead
        dashboard
        kpi
        project overview
        opportunity
        budget
        analytic
        odoo profitability module
        odoo project profitability
        odoo margin tracking
        odoo cost tracking module
        odoo profit analysis
        odoo project margin
        odoo crm profitability
        odoo financial tracking
        odoo profit management
        odoo cost control
        project profitability tracking
        margin analysis software odoo
        profit margin tracking system
        business profitability tools
        project margin analysis
        profit optimization software
        margin control system
        profit tracking software
        gross margin tracking
        net profit analysis
        project cost tracking odoo
        project financial management
        project budget tracking
        project revenue tracking
        cost vs revenue analysis
        project expense tracking
        project performance metrics
        project financial dashboard
        project cost control system
        project accounting insights
        crm profit tracking
        lead profitability analysis
        sales margin tracking
        crm cost analysis
        deal profitability tracking
        sales performance profitability
        revenue vs cost crm
        crm financial insights
        opportunity profit analysis
        sales cost control
        odoo dashboard kpi
        profitability dashboard odoo
        financial dashboard odoo
        kpi tracking system
        business performance dashboard
        margin dashboard
        cost analysis dashboard
        revenue analytics odoo
        financial reporting dashboard
        real time profit tracking
        profitability alerts
        cost overrun alerts
        margin warning system
        automated financial alerts
        project risk alerts
        budget overrun notification
        financial monitoring system
        profit risk management
        automated cost tracking
        smart financial alerts
        odoo crm project integration
        odoo project module extension
        odoo business intelligence
        odoo financial analytics
        odoo custom dashboard
        odoo automation module
        odoo reporting tools
        odoo enterprise addon
        odoo community module
        odoo workflow automation
        agency profitability tracking
        consulting profit management
        service business profitability
        it project cost tracking
        software project margin
        professional services analytics
        resource cost tracking
        time and cost management
        project based business tools
        service margin optimization
        track project profitability in odoo
        how to measure project margin odoo
        odoo module for cost and revenue tracking
        best odoo profitability module
        odoo solution for project cost control
        crm to project profitability tracking
        odoo tool for margin analysis
        project profit dashboard odoo
        odoo app for financial performance
        profit tracking from lead to project
    """,
    'depends': [
        'project',
        'account',
        'sale_management',
        'sale_crm',  # Links SO to CRM lead (opportunity_id, expected_revenue)
        'crm',       # For lead-centric profitability (Status → Customer → Lead → SO → Invoice)
        'purchase',  # For cost from related POs
    ],
    'external_dependencies': {
        'python': ['xlsxwriter'],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/scheduled_actions.xml',
        'views/lead_profitability_views.xml',
        'views/crm_lead_views.xml',
        'views/project_profitability_views.xml',
        'views/project_project_views.xml',
        'views/profitability_alert_views.xml',
        'views/dashboard_action.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'project_profitability/static/src/scss/profitability_dashboard.scss',
            'project_profitability/static/src/js/profitability_dashboard.js',
            'project_profitability/static/src/xml/profitability_dashboard.xml',
        ],
    },
    'demo': [
        'demo/demo_data.xml',
    ],
    'images': [
        'static/description/main_screen.gif'
    ],
    'price': 19.90,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
