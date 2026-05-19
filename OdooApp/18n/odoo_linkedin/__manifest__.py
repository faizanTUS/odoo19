{
    'name': 'LinkedIn Integration',
    'version': '18.0',
    'summary': """Integrates LinkedIn with HR Recruitment
                Odoo LinkedIn Integration
                LinkedIn Odoo Recruitment
                LinkedIn HR Integration Odoo
                Odoo Recruitment LinkedIn Connector
                LinkedIn Job Posting Odoo
                Odoo HR LinkedIn Sync
                LinkedIn API Integration with Odoo
                Odoo Recruitment Automation
                LinkedIn Applicant Tracking Odoo
                LinkedIn to Odoo Resume Import
                How to integrate LinkedIn with Odoo HR
                Post jobs on LinkedIn from Odoo
                LinkedIn candidate import in Odoo
                Sync LinkedIn applicants with Odoo
                Automate LinkedIn job applications to Odoo
                LinkedIn recruitment pipeline in Odoo
                LinkedIn API Odoo recruitment module
                Odoo HRMS LinkedIn plugin
                Odoo recruitment with LinkedIn profiles
                LinkedIn CRM integration with Odoo HR
                """,
    'description': """Basic module for LinkedIn-HR Recruitment connector
                Odoo LinkedIn Integration
                LinkedIn Odoo Recruitment
                LinkedIn HR Integration Odoo
                Odoo Recruitment LinkedIn Connector
                LinkedIn Job Posting Odoo
                Odoo HR LinkedIn Sync
                LinkedIn API Integration with Odoo
                Odoo Recruitment Automation
                LinkedIn Applicant Tracking Odoo
                LinkedIn to Odoo Resume Import
                How to integrate LinkedIn with Odoo HR
                Post jobs on LinkedIn from Odoo
                LinkedIn candidate import in Odoo
                Sync LinkedIn applicants with Odoo
                Automate LinkedIn job applications to Odoo
                LinkedIn recruitment pipeline in Odoo
                LinkedIn API Odoo recruitment module
                Odoo HRMS LinkedIn plugin
                Odoo recruitment with LinkedIn profiles
                LinkedIn CRM integration with Odoo HR
                    
    """,
    'category': 'Generic Modules/Human Resources',
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com',
    'depends': ['base', 'hr', 'hr_recruitment', 'auth_oauth'],
    'license': 'AGPL-3',
    'data': [
        'data/auth_linkedin_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/multiple_user_selection.xml',
        'views/hr_job_linkedin.xml',
        'views/oauth_view.xml',
        'views/res_users.xml',

    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'application': True,
    'auto_install': False,
    'price': 49.99,
    'currency': 'USD',
}
