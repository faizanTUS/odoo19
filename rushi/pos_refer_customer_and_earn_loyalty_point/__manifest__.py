# Part of Odoo.See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'POS Refer Customer And Earn Loyalty Point',
    "description": """
    The POS Refer Customer And Earn Referral Loyalty Point module is designed to enhance customer engagement and retention by introducing a robust referral and loyalty point system directly within the Point of Sale (POS) interface. This module empowers businesses to reward customers for referring new buyers and incentivizes both referrers and referred customers through a flexible loyalty program.
    POS refer a friend program
    POS customer referral system
    POS loyalty points module
    POS referral rewards program
    Refer and earn loyalty POS
    POS customer rewards system
    POS loyalty program integration
    POS referral bonus software
    Odoo POS referral module
    POS customer loyalty points system
    POS reward points software
    Refer customer and earn points POS
    POS referral and loyalty program
    Retail POS loyalty points solution
    POS referral management system
    POS customer engagement module
    Loyalty rewards for POS customers
    POS reward and referral app
    POS customer retention solution
    POS referral and earn software
    Odoo19
    Odoo18
    Odoo17
    Odoo16
    TUS
    tus
    techultra solutions
    techultra
    techultra solutions private limited
    """,
"summary": """Boost customer retention with POS referral and loyalty points. Reward referrers and new customers instantly at checkout.
    POS refer a friend program
    POS customer referral system
    POS loyalty points module
    POS referral rewards program
    Refer and earn loyalty POS
    POS customer rewards system
    POS loyalty program integration
    POS referral bonus software
    Odoo POS referral module
    POS customer loyalty points system
    POS reward points software
    Refer customer and earn points POS
    POS referral and loyalty program
    Retail POS loyalty points solution
    POS referral management system
    POS customer engagement module
    Loyalty rewards for POS customers
    POS reward and referral app
    POS customer retention solution
    POS referral and earn software
    Odoo19
    Odoo18
    Odoo17
    Odoo16
    TUS
    tus
    techultra solutions
    techultra
    techultra solutions private limited
    """,
    'version': '19.0',
    'category': 'Sales/Loyalty',
    "author": "TechUltra Solutions Private Limited",
    "website": "https://www.techultrasolutions.com",
    "license": "OPL-1",
    'depends': ['base', 'loyalty', 'point_of_sale', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        # 'data/cron_job.xml',
        'data/sequence_code.xml',
        'data/membership_level.xml',
        'data/send_referral_code_mail.xml',
        'views/res_partner.xml',
        'views/res_config_settings.xml',
        'views/loyalty_card.xml',
        'views/loyalty_referral.xml',
    ],
    "images": [
        "static/description/icon.png",
        "static/description/main_screen.gif",
    ],
    'post_init_hook': '_generate_referral_code',
    'installable': True,
    'application': False,
}
