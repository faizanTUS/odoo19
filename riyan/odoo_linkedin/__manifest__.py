# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'LinkedIn Integration',
    'version': '19.0.0.0',
    'images': ['static/description/banner.jpg'],
    'summary': 'Integrates LinkedIn with HR Recruitment',
    'description': 'Basic module for LinkedIn-HR Recruitment connector',
    'category': 'Generic Modules/Human Resources',
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com',
    'depends': ['base', 'hr', 'hr_recruitment', 'auth_oauth'],
    'license': 'OPL-1',
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
    'summary': 'linkedin job post and linkedin normal post module where company can send updates to linkedin page',
    'description': """
        This module allows to post to linkedin and allow the job post by normal post form you can set url and images to attract the audience.
    """,
}
