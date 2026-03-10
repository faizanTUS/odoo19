# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'POS Loyalty birthday reward',
    "summary": """POS Loyalty birthday reward  simplifies the generation, management,
               and redemption of coupon codes in Odoo. It enhances customer satisfaction by emailing codes directly
               to customers and enabling easy redemption through the POS system, with clear receipts and notifications
               "for a seamless experience.
               POS birthday reward
                Birthday loyalty program Odoo
                Odoo POS coupon generation
                Birthday coupon automation
                POS customer reward system
                Loyalty coupon email Odoo
                Birthday discount in POS
                POS voucher redemption
                Odoo birthday promotion
                Customer reward management
                Seamless coupon redemption
                POS printed coupon receipt
                Auto-send loyalty codes
                POS reward notification
                Birthday voucher email
                Reward redemption at checkout
                Easy POS coupon scanning
                Personalized reward delivery
                Automated loyalty incentives
                POS birthday celebration offer
                Coupon code generation Odoo
                Automated email campaign Odoo
                Birthday date trigger Odoo
                POS loyalty integration
                Reward workflow Odoo POS
                Odoo CRM loyalty sync
                POS loyalty rules configuration
                Customer-based reward automation
               """,
    "description": """ POS Loyalty birthday reward simplifies the process
                of generating, managing, and redeeming coupon codes in Odoo.
                It is designed to improve customer satisfaction and boost operational 
                efficiency by allowing businesses to send coupon codes directly to customers via email.
                The module also enables seamless redemption through the Point of Sale (POS) system.
                Detailed receipts and notifications ensure clarity and a smooth user experience.
                POS birthday reward
                Birthday loyalty program Odoo
                Odoo POS coupon generation
                Birthday coupon automation
                POS customer reward system
                Loyalty coupon email Odoo
                Birthday discount in POS
                POS voucher redemption
                Odoo birthday promotion
                Customer reward management
                Seamless coupon redemption
                POS printed coupon receipt
                Auto-send loyalty codes
                POS reward notification
                Birthday voucher email
                Reward redemption at checkout
                Easy POS coupon scanning
                Personalized reward delivery
                Automated loyalty incentives
                POS birthday celebration offer
                Coupon code generation Odoo
                Automated email campaign Odoo
                Birthday date trigger Odoo
                POS loyalty integration
                Reward workflow Odoo POS
                Odoo CRM loyalty sync
                POS loyalty rules configuration
                Customer-based reward automation
    """,
    'version': '18.0',
    "author": "TechUltra Solutions Private Limited",
    "company": "TechUltra Solutions Private Limited",
    "website": "https://www.techultrasolution.com",
    'category': 'Sales/Loyalty',
    "images": [
        "static/description/icon.png",
        "static/description/main_screen.gif",
    ],
    'depends': ['base', 'loyalty', 'point_of_sale', 'mail'],
    'data': [
        # 'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'data/birthday_mail.xml',
        'views/loyalty_program_views.xml',
        'views/res_partner_views.xml',
    ],
     'license': 'OPL-1',
    "price": 20,
    "currency": "USD",
    'installable': True,
    'application': True,
    'auto_install': False
}