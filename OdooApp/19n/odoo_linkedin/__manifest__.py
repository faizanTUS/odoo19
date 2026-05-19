# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'LinkedIn Integration',
    'version': '19.0.0.0',
    'summary': """linkedin job post and linkedin normal post module where company can send updates to linkedin page


        tus
        techultra
        techultra_private_limited_solution
        linkedin
        linkedin integration
        odoo linkedin
        linkedin connector
        social media
        social media integration
        odoo social media
        linkedin marketing
        linkedin recruitment
        linkedin job posting
        hr recruitment
        odoo hr
        odoo marketing
        post scheduler
        company page integration
        professional networking
        linkedin automation
        linkedin api
        odoo connector
        linkedin posts
        linkedin articles
        linkedin image posts
        Odoo LinkedIn Integration
        LinkedIn Odoo Connector
        LinkedIn Integration Module for Odoo
        Odoo Social Media Integration
        LinkedIn API Integration Odoo
        Odoo Recruitment LinkedIn Integration
        Manage LinkedIn from Odoo
        LinkedIn Company Page Integration
        LinkedIn Member Account Integration
        Odoo HR LinkedIn Connector
        Odoo Job Posting to LinkedIn
        Share LinkedIn posts from Odoo
        LinkedIn article posting via Odoo
        LinkedIn image post integration
        Odoo marketing automation LinkedIn
        Odoo social media management module
        Odoo LinkedIn posting app
        LinkedIn marketing tool for Odoo
        Odoo social media scheduler
        Odoo LinkedIn automation
        LinkedIn content manager for Odoo
        Odoo LinkedIn profile integration
        Odoo company branding on LinkedIn
        LinkedIn lead generation Odoo
        Odoo LinkedIn communication tool
        Odoo social network integration module
        Odoo HR LinkedIn posting tool
        Odoo recruitment social media module
        Post to LinkedIn from Odoo
        Odoo multi-account LinkedIn integration
        LinkedIn business page integration Odoo
        Odoo LinkedIn dashboard
        LinkedIn analytics in Odoo
        Odoo employee branding module
        Odoo job publishing on LinkedIn
        Odoo LinkedIn API connector
        Odoo post scheduler LinkedIn
        LinkedIn article sharing Odoo module
        LinkedIn image post-integration with Odoo
        Odoo job seeker connection tool
        Odoo to LinkedIn product/service posts
        Odoo corporate culture LinkedIn posting

    """,
    'description': """
        This module allows to post to linkedin and allow the job post by normal post form you can set url and images to attract the audience.

        tus
        techultra
        techultra_private_limited_solution
        linkedin
        linkedin integration
        odoo linkedin
        linkedin connector
        social media
        social media integration
        odoo social media
        linkedin marketing
        linkedin recruitment
        linkedin job posting
        hr recruitment
        odoo hr
        odoo marketing
        post scheduler
        company page integration
        professional networking
        linkedin automation
        linkedin api
        odoo connector
        linkedin posts
        linkedin articles
        linkedin image posts
        Odoo LinkedIn Integration
        LinkedIn Odoo Connector
        LinkedIn Integration Module for Odoo
        Odoo Social Media Integration
        LinkedIn API Integration Odoo
        Odoo Recruitment LinkedIn Integration
        Manage LinkedIn from Odoo
        LinkedIn Company Page Integration
        LinkedIn Member Account Integration
        Odoo HR LinkedIn Connector
        Odoo Job Posting to LinkedIn
        Share LinkedIn posts from Odoo
        LinkedIn article posting via Odoo
        LinkedIn image post integration
        Odoo marketing automation LinkedIn
        Odoo social media management module
        Odoo LinkedIn posting app
        LinkedIn marketing tool for Odoo
        Odoo social media scheduler
        Odoo LinkedIn automation
        LinkedIn content manager for Odoo
        Odoo LinkedIn profile integration
        Odoo company branding on LinkedIn
        LinkedIn lead generation Odoo
        Odoo LinkedIn communication tool
        Odoo social network integration module
        Odoo HR LinkedIn posting tool
        Odoo recruitment social media module
        Post to LinkedIn from Odoo
        Odoo multi-account LinkedIn integration
        LinkedIn business page integration Odoo
        Odoo LinkedIn dashboard
        LinkedIn analytics in Odoo
        Odoo employee branding module
        Odoo job publishing on LinkedIn
        Odoo LinkedIn API connector
        Odoo post scheduler LinkedIn
        LinkedIn article sharing Odoo module
        LinkedIn image post-integration with Odoo
        Odoo job seeker connection tool
        Odoo to LinkedIn product/service posts
        Odoo corporate culture LinkedIn posting

    """,
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

}
