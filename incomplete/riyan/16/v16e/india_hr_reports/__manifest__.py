# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    "name": "HR India Reports for | Attendance, Leave, Payroll, Recruitment & HR MIS Reports",
    "version": "16.0.0.0",
    "category": "Human Resources",
    "summary": """HR India Reports for | Attendance, Leave, Payroll, Recruitment & HR MIS Reports HR–aligned reporting hub: shared XLSX/PDF exports, cockpit, core HR reports
     Comprehensive HR reporting hub for Indian localization, providing XLSX and PDF exports for Attendance, Leave, Payroll,
     Recruitment, Expenses, Fleet, and Planning with an interactive cockpit dashboard

    tus
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited
    India
    HR
    Payroll
    Reports
    Statutory
    PF
    ESI
    Attendance
    XLSX, Dashboard
    Compliance
    MIS
    Recruitment
    Expense
    Odoo India HR Reports
    Indian Payroll Reports Odoo
    Statutory Reports India
    HR MIS Reports Odoo
    Odoo Payroll XLSX Export
    Indian Compliance Reports
    Odoo HR Dashboard
    Attendance and Leave Reports Odoo
    PF Register Report (Provident Fund)
    ESI Register Report (Employee State Insurance)
    PT Register (Professional Tax)
    LWF Register (Labour Welfare Fund)
    TDS Summary Report
    Income Tax Reports India
    Odoo Indian Payroll Statutory
    HR Reporting Cockpit
    Recruitment Analysis Report
    Expense Summary XLSX
    Fleet Management Reports
    Planning and Shift Reports
    Professional PDF HR Templates
    Employee Attendance Summary
    Leave Balance Report Odoo
    Odoo XLSX Reports
    Odoo PDF Reports
    Multi-Company HR Reports
    Custom HR Reporting Hub
    Odoo 16 HR Reports
    Excel Export for Payroll
    """,
    "description": """
India HR Reports is a centralized reporting solution tailored for Indian businesses, consolidating all essential HR data
into professional, ready-to-use reports. This module provides a unified interface ("Reporting Cockpit") to generate
detailed insights across multiple HR domains.

Designed to streamline HR MIS (Management Information System) reporting, this module ensures compliance and data-driven
decision-making for Indian HR departments.

    tus
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited
    India
    HR
    Payroll
    Reports
    Statutory
    PF
    ESI
    Attendance
    XLSX, Dashboard
    Compliance
    MIS
    Recruitment
    Expense
    Odoo India HR Reports
    Indian Payroll Reports Odoo
    Statutory Reports India
    HR MIS Reports Odoo
    Odoo Payroll XLSX Export
    Indian Compliance Reports
    Odoo HR Dashboard
    Attendance and Leave Reports Odoo
    PF Register Report (Provident Fund)
    ESI Register Report (Employee State Insurance)
    PT Register (Professional Tax)
    LWF Register (Labour Welfare Fund)
    TDS Summary Report
    Income Tax Reports India
    Odoo Indian Payroll Statutory
    HR Reporting Cockpit
    Recruitment Analysis Report
    Expense Summary XLSX
    Fleet Management Reports
    Planning and Shift Reports
    Professional PDF HR Templates
    Employee Attendance Summary
    Leave Balance Report Odoo
    Odoo XLSX Reports
    Odoo PDF Reports
    Multi-Company HR Reports
    Custom HR Reporting Hub
    Odoo 16 HR Reports
    Excel Export for Payroll

""",
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com",
    "depends": [
        "hr", "web", "hr_attendance", "hr_expense", "fleet", "hr_holidays",
        "hr_payroll", "l10n_in_hr_payroll",
        "planning", "hr_recruitment",
    ],
    "external_dependencies": {"python": ["xlsxwriter"]},
    "data": [
        # hr_in_reports
        "hr_in_reports/data/hr_in_reports_config.xml",
        "hr_in_reports/security/hr_in_reports_security.xml",
        "hr_in_reports/security/ir.model.access.csv",
        "hr_in_reports/reports/hr_in_report_pdf_professional.xml",
        "hr_in_reports/reports/hr_in_report_pdf_templates.xml",
        "hr_in_reports/views/wizard_hub_reports_views.xml",
        "hr_in_reports/views/hr_in_reports_cockpit_action.xml",
        "hr_in_reports/views/hr_in_reports_menus.xml",

        # hr_in_reports_attendance
        "hr_in_reports_attendance/security/ir.model.access.csv",
        "hr_in_reports_attendance/reports/attendance_pdf.xml",
        "hr_in_reports_attendance/views/wizard_attendance_views.xml",

        # hr_in_reports_enterprise_prompt
        "hr_in_reports_enterprise_prompt/security/ir.model.access.csv",
        "hr_in_reports_enterprise_prompt/views/hr_in_reports_enterprise_notice_views.xml",
        "hr_in_reports_enterprise_prompt/views/hr_in_reports_enterprise_notice_menus.xml",

        # hr_in_reports_expense
        "hr_in_reports_expense/security/ir.model.access.csv",
        "hr_in_reports_expense/reports/expense_pdf.xml",
        "hr_in_reports_expense/views/wizard_expense_views.xml",

        # hr_in_reports_fleet
        "hr_in_reports_fleet/security/ir.model.access.csv",
        "hr_in_reports_fleet/reports/fleet_pdf.xml",
        "hr_in_reports_fleet/views/wizard_fleet_views.xml",

        # hr_in_reports_leave
        "hr_in_reports_leave/security/ir.model.access.csv",
        "hr_in_reports_leave/reports/leave_pdf.xml",
        "hr_in_reports_leave/views/wizard_leave_views.xml",

        # hr_in_reports_payroll
        "hr_in_reports_payroll/security/ir.model.access.csv",
        "hr_in_reports_payroll/data/payroll_disable_ce_placeholder_menu.xml",
        "hr_in_reports_payroll/reports/payroll_pdf.xml",
        "hr_in_reports_payroll/views/wizard_payroll_views.xml",

        # hr_in_reports_payroll_in
        "hr_in_reports_payroll_in/data/payroll_reporting_menu_order.xml",
        "hr_in_reports_payroll_in/security/ir.model.access.csv",
        "hr_in_reports_payroll_in/reports/payroll_in_pdf.xml",
        "hr_in_reports_payroll_in/views/wizard_payroll_in_views.xml",

        # hr_in_reports_planning
        "hr_in_reports_planning/security/ir.model.access.csv",
        "hr_in_reports_planning/reports/planning_pdf.xml",
        "hr_in_reports_planning/views/wizard_planning_views.xml",

        # hr_in_reports_recruitment
        "hr_in_reports_recruitment/security/ir.model.access.csv",
        "hr_in_reports_recruitment/data/recruitment_analysis_list_first.xml",
        "hr_in_reports_recruitment/reports/recruitment_pdf.xml",
        "hr_in_reports_recruitment/views/wizard_recruitment_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # hr_in_reports
            "india_hr_reports/static/hr_in_reports/static/src/scss/hr_in_cockpit_dashboard.scss",
            "india_hr_reports/static/hr_in_reports/static/src/cockpit/cockpit_action.js",
        ],
        "web.report_assets_common": [
            # hr_in_reports
            "india_hr_reports/static/hr_in_reports/static/src/scss/hr_in_report_pdf_professional.scss",

            # hr_in_reports_leave
            "india_hr_reports/static/hr_in_reports_leave/static/src/scss/report_leave_pdf.scss",
        ],
    },
    "images": [
        "static/description/main_screen.gif",
    ],
    'license': 'OPL-1',
    "price": 110.00,
    "currency": 'USD',
    "installable": True,
    "application": True,
    "auto_install": False,
}
