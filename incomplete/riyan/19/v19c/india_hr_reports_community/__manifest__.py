# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    "name": "India HR Reports (Community) | All-in-One HR MIS Hub: Dashboard, Attendance, Leave, Recruitment, Expense & Fleet (XLSX/PDF)",
    "version": "19.0.0.0",
    "category": "Human Resources",
    "summary": """Community HR reporting hub: XLSX/PDF exports, cockpit dashboard, core HR reports
     Comprehensive HR reporting hub for Odoo Community, providing XLSX and PDF exports for
     Attendance, Leave, Recruitment, Expenses, and Fleet with an interactive cockpit dashboard.

    tus
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited
    India
    HR
    Reports
    MIS
    Attendance
    Leave
    Recruitment
    Expense
    Fleet
    XLSX, Dashboard
    Compliance
    Community
    Odoo Community HR Reports
    Indian HR Reports Odoo
    Attendance and Leave Reports Odoo
    HR MIS Reports Odoo
    Odoo HR Dashboard
    HR Reporting Cockpit
    Recruitment Analysis Report
    Expense Summary XLSX
    Fleet Management Reports
    Professional PDF HR Templates
    Employee Attendance Summary
    Leave Balance Report Odoo
    Odoo XLSX Reports
    Odoo PDF Reports
    Multi-Company HR Reports
    Custom HR Reporting Hub
    Odoo 19 HR Reports Community
    """,
    "description": """
India HR Reports (Community) is a centralized reporting solution tailored for Indian businesses
running Odoo Community Edition, consolidating essential HR data into professional, ready-to-use
reports. This module provides a unified interface ("Reporting Cockpit") to generate detailed
insights across the HR domains available in Community: Attendance, Leave, Recruitment,
Expense, and Fleet.

    tus
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited
    India
    HR
    Reports
    MIS
    Attendance
    Leave
    Recruitment
    Expense
    Fleet
    XLSX, Dashboard
    Compliance
    Community
    Odoo Community HR Reports
    Indian HR Reports Odoo
    Attendance and Leave Reports Odoo
    HR MIS Reports Odoo
    Odoo HR Dashboard
    HR Reporting Cockpit
    Recruitment Analysis Report
    Expense Summary XLSX
    Fleet Management Reports
    Professional PDF HR Templates
    Employee Attendance Summary
    Leave Balance Report Odoo
    Odoo XLSX Reports
    Odoo PDF Reports
    Multi-Company HR Reports
    Custom HR Reporting Hub
    Odoo 19 HR Reports Community

""",
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com",
    "depends": [
        "hr",
        "web",
        "hr_attendance",
        "hr_expense",
        "fleet",
        "hr_holidays",
        "hr_recruitment",
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

        # hr_in_reports_recruitment
        "hr_in_reports_recruitment/security/ir.model.access.csv",
        "hr_in_reports_recruitment/data/recruitment_analysis_list_first.xml",
        "hr_in_reports_recruitment/reports/recruitment_pdf.xml",
        "hr_in_reports_recruitment/views/wizard_recruitment_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # hr_in_reports
            "india_hr_reports_community/static/hr_in_reports/static/src/scss/hr_in_cockpit_dashboard.scss",
            "india_hr_reports_community/static/hr_in_reports/static/src/cockpit/cockpit_action.js",
        ],
        "web.report_assets_common": [
            # hr_in_reports
            "india_hr_reports_community/static/hr_in_reports/static/src/scss/hr_in_report_pdf_professional.scss",

            # hr_in_reports_leave
            "india_hr_reports_community/static/hr_in_reports_leave/static/src/scss/report_leave_pdf.scss",
        ],
    },
    "images": [
        "static/description/main_screen.gif",
    ],
    'license': 'OPL-1',
    "price": 79.90,
    "currency": 'USD',
    "installable": True,
    "application": True,
    "auto_install": False,
}
