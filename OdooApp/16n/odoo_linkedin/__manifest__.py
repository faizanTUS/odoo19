{
    'name': 'LinkedIn Integration',
    'version': '16.0.1.0.0',
    'summary': 'linkedin job post and linkedin normal post module where company can send updates to linkedin page',
    'description': """
        This module allows to post to linkedin and allow the job post by normal post form you can set url and images to attract the audience.
    """,
    'category': 'Generic Modules/Human Resources',
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com',
    'depends': [
        'base',
        'hr',
        'hr_recruitment',
        'auth_oauth'
    ],
    'data': [
        'data/auth_linkedin_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/multiple_user_selection.xml',
        'views/hr_job_linkedin.xml',
        'views/oauth_view.xml',
        'views/res_users.xml',
    ],
    'images': [
        'static/description/main_screen.gif',
        'static/description/banner.jpg',
    ],
    'application': True,
    'auto_install': False,
    'price': 49.99,
    'currency': 'USD',
    'license': 'OPL-1',
}
