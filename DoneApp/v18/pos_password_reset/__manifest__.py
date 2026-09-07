# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'POS Cashier Password Reset | Self-Service PIN Reset | Odoo Point of Sale Security',
    'summary': """
    Are you frustrated because you can't reset passwords? Cashiers keep asking you for their password repeatedly, do you want Cashiers to reset their passwords on their own? So,  Your wish has come true because we have developed a POS password reset app through which Cashiers can reset their passwords anytime.For more information about its features, please scroll down.
    Tired of resetting cashier passwords again and again? Empower your cashiers with the ability to reset their own passwords securely and effortlessly! Our POS Password Reset app allows cashiers to reset their POS login credentials without needing manager intervention.
    POS password reset
    Odoo POS password
    Reset cashier password
    Self-service password reset
    POS login reset Odoo
    Odoo POS security
    Odoo password reset module
    Cashier self-reset password
    Allow cashiers to reset POS passwords in Odoo
    How to reset cashier password in Odoo POS
    POS module to reset forgotten passwords
    Odoo POS cashier login password reset app
    Easy password reset for POS users in Odoo
    POS password recovery without admin in Odoo
    Odoo POS password reset without manager access
    POS password reset feature for cashiers
    """,
    'description':"""
    Are you constantly being interrupted by cashiers asking for password resets? Does your store's workflow get disrupted when a cashier forgets their password?
    With our POS Password Reset app, those days are over!
    This module allows cashiers to reset their passwords on their own, directly from the POS interface. No more calls, no more delays, and no more stress for managers and admins.
    Whether you're managing a single store or a retail chain, this app helps you maintain smooth POS operations while giving your team more autonomy.
    Scroll down to explore the full list of features and see how this module can make your life easier.
    POS password reset
    Odoo POS password
    Reset cashier password
    Self-service password reset
    POS login reset Odoo
    Odoo POS security
    Odoo password reset module
    Cashier self-reset password
    Allow cashiers to reset POS passwords in Odoo
    How to reset cashier password in Odoo POS
    POS module to reset forgotten passwords
    Odoo POS cashier login password reset app
    Easy password reset for POS users in Odoo
    POS password recovery without admin in Odoo
    Odoo POS password reset without manager access
    POS password reset feature for cashiers
    """,
    'version': '18.0.0.0',
    'category': 'Point of Sale',
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'depends': ['point_of_sale', 'hr'],
    'data': [],
    'assets': {
        'point_of_sale._assets_pos': [
            "pos_password_reset/static/src/app/reset_button/reset_button.js",
            "pos_password_reset/static/src/app/reset_button/reset_button.xml",
            "pos_password_reset/static/src/app/reset_popup/reset_password.js",
            "pos_password_reset/static/src/app/reset_popup/reset_popup.xml",
            'pos_password_reset/static/src/app/successfull_popup/successful_popup.js',
            'pos_password_reset/static/src/app/successfull_popup/successful_template.xml',
        ],
    },

    "images": ['static/description/main_screen.gif'],
    'license': 'OPL-1',
    "price": 15.00,
    "currency": "USD",
    'installable': True,
    'application': True,
    'auto_install': False
}
