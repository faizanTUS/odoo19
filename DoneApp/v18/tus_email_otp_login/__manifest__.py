# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Secure Email OTP Verification | Email OTP Security | User Verification via Email OTP',
    'version': '18.0.0.0',
    'author': 'TechUltra Solutions Private Limited',
    'category': 'Tools',
    'website': 'https://www.techultrasolutions.com',
    "company": "TechUltra Solutions Private Limited",
    'summary': """
    Secure Email OTP Verification enhances Odoo authentication by adding email-based OTP verification for secure user registration, login, and identity validation.
    Secure Email OTP Verification
    Odoo Email OTP Verification
    Odoo Two Factor Authentication
    Odoo OTP Authentication
    Odoo User Verification
    Odoo Email Authentication
    Odoo Login Security
    Odoo User Access Security
    Odoo Account Security
    Odoo Email Verification
    Odoo User Registration Security
    Odoo Login Verification
    Odoo Authentication Module
    Odoo Security Module
    Odoo User Management
    Odoo Access Control
    Odoo Identity Verification
    Email OTP Security
    Email Based Authentication
    One Time Password Verification
    OTP Verification System
    Secure User Authentication
    User Identity Verification
    Email Security Verification
    OTP Expiry Management
    OTP Verification History
    User Login Protection
    Secure Login System
    Digital Authentication Security
    Enterprise User Security
    """,
    'description': """
    This module provides a secure One-Time Password (OTP) verification system in Odoo, allowing users to verify their identity through email during critical authentication processes. It also enables administrators to monitor OTP activities, manage verification records, and improve overall access security.
    Secure Email OTP Verification
    Odoo Email OTP Verification
    Odoo Two Factor Authentication
    Odoo OTP Authentication
    Odoo User Verification
    Odoo Email Authentication
    Odoo Login Security
    Odoo User Access Security
    Odoo Account Security
    Odoo Email Verification
    Odoo User Registration Security
    Odoo Login Verification
    Odoo Authentication Module
    Odoo Security Module
    Odoo User Management
    Odoo Access Control
    Odoo Identity Verification
    Email OTP Security
    Email Based Authentication
    One Time Password Verification
    OTP Verification System
    Secure User Authentication
    User Identity Verification
    Email Security Verification
    OTP Expiry Management
    OTP Verification History
    User Login Protection
    Secure Login System
    Digital Authentication Security
    Enterprise User Security
    """,
    'depends': ['base', 'mail', 'web', 'website', 'auth_signup', 'auth_totp'],
    'data': [
        'data/data.xml',
        'data/cron.xml',
        'security/ir.model.access.csv',
        'security/security_group.xml',
        'wizard/email_auth_otp_wizard.xml',
        'views/otp_verification.xml',
        'views/login_view.xml',
        'views/otp_signup.xml',
        'views/res_config_settings_inherit.xml',
        'views/res_users_inherited_views.xml',
        'views/email_2fa_form_template_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/tus_email_otp_login/static/src/js/login.js',
        ],
        'web.assets_backend': [
            '/tus_email_otp_login/static/src/js/login.js',
        ],
    },
    'images': [
        'static/description/main_screen.gif',
    ],
    'price': 20.01,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    "application": False,
}
