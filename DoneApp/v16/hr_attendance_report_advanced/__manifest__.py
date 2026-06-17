# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Employee Attendance Reports | Attendance Summary | HR Analytics',
    'version': '16.0.0.0',
    'category': 'Human Resources',
    'summary': """
    Employee Attendance Reports | Attendance Summary | HR Analytics is a comprehensive HR attendance reporting solution for Odoo that helps organizations analyze employee attendance through detailed, summary, matrix, and department-wise reports. It provides professional PDF reports, attendance status management, report configuration options, and data import utilities, enabling HR teams to streamline attendance monitoring, payroll preparation, and compliance reporting.
    Odoo Reporting Module
    Odoo HR Reporting
    Odoo Workforce Reports
    Odoo Analytics Dashboard
    Odoo PDF Reports
    Odoo Data Analysis Tool
    Employee Report Generator
    Monthly Report Generator
    Detailed Report PDF
    Summary Report PDF
    Printable Business Reports
    Automated Report Generation
    Matrix View Reports
    Employee Matrix View
    Date Wise Matrix Report
    Summary Matrix View
    Calendar Based Reports
    Analytics Dashboard
    Performance Analytics
    Trend Analysis Reports
    Data Visualization Dashboard
    Management Reports
    Employee Wise Reports
    Department Wise Reports
    Department Summary Reports
    Workforce Analytics
    Data Import Tool
    Bulk Data Import
    Status Configuration
    Report Configuration
    Custom Report Builder
    Working Hours Report
    Overtime Analysis
    Time Tracking Reports
    Daily Time Summary
    Odoo Attendance Reports
    Attendance Analytics Odoo
    Attendance Matrix View
    Attendance Summary Report
    Attendance Report PDF
    odoo18
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'description': """
    Employee Attendance Reports | Attendance Summary | HR Analytics extends Odoo's HR Attendance functionality with advanced reporting, analytics, and configuration capabilities. The module allows HR managers to generate detailed attendance reports in multiple formats, including employee-wise, department-wise, summary, and matrix views. Reports are generated in professional PDF format, making them suitable for payroll processing, audits, and management reviews. It also includes attendance data import tools, customizable report settings, and attendance status management features. With all reporting and configuration options available from a centralized menu, organizations can efficiently monitor workforce attendance and improve HR decision-making.
    Odoo Reporting Module
    Odoo HR Reporting
    Odoo Workforce Reports
    Odoo Analytics Dashboard
    Odoo PDF Reports
    Odoo Data Analysis Tool
    Employee Report Generator
    Monthly Report Generator
    Detailed Report PDF
    Summary Report PDF
    Printable Business Reports
    Automated Report Generation
    Matrix View Reports
    Employee Matrix View
    Date Wise Matrix Report
    Summary Matrix View
    Calendar Based Reports
    Analytics Dashboard
    Performance Analytics
    Trend Analysis Reports
    Data Visualization Dashboard
    Management Reports
    Employee Wise Reports
    Department Wise Reports
    Department Summary Reports
    Workforce Analytics
    Data Import Tool
    Bulk Data Import
    Status Configuration
    Report Configuration
    Custom Report Builder
    Working Hours Report
    Overtime Analysis
    Time Tracking Reports
    Daily Time Summary
    Odoo Attendance Reports
    Attendance Analytics Odoo
    Attendance Matrix View
    Attendance Summary Report
    Attendance Report PDF
    odoo18
    tus
    TUS
    Techultra solutions
    Techultra solutions private solutions
    techultra solutions private limited
    """,
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com/',
    'depends': ['hr', 'hr_attendance', 'web', 'hr_holidays'],
    'data': [
        'security/attendance_report_security.xml',
        'security/ir.model.access.csv',
        'data/attendance_status_data.xml',
        'data/mail_template_data.xml',
        'data/report_paperformat_data.xml',
        'views/attendance_config_views.xml',
        'views/hr_attendance_status_views.xml',
        'views/hr_attendance_report_views.xml',
        'views/hr_attendance_tree_views.xml',  # Load last to override gantt view modes
        'views/attendance_dashboard_views.xml',
        'views/attendance_matrix_views.xml',
        'views/attendance_import_wizard_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_department_views.xml',
        'views/attendance_analytics_views.xml',
        'reports/attendance_report.xml',
        'reports/analytics_report.xml',
        'views/templates.xml',
        'views/menuitems.xml',
        'views/hr_attendance_action_override.xml',  # Load last to override enterprise gantt views
    ],
    'assets': {
        'web.assets_backend': [
            'hr_attendance_report_advanced/static/src/css/attendance_report.css',
            'hr_attendance_report_advanced/static/src/css/analytics_dashboard.css',
            'hr_attendance_report_advanced/static/src/css/attendance_matrix.css',
        ],
        'web.assets_qweb': [
            'hr_attendance_report_advanced/static/src/xml/attendance_report.xml',
            'hr_attendance_report_advanced/static/src/xml/analytics_dashboard.xml',
            'hr_attendance_report_advanced/static/src/xml/attendance_matrix.xml',
        ],
    },
    "images": [
        "static/description/main_screen.gif",
    ],
    'external_dependencies': {
        'python': ['xlsxwriter'],
    },
    'post_init_hook': 'post_init_hook',
    'price': 19.84,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    "license": "OPL-1",
    "application": False,
}
