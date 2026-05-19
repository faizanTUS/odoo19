# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'POS Loyalty birthday reward',
    "summary": """POS Loyalty birthday reward  simplifies the generation, management,
               and redemption of coupon codes in Odoo. It enhances customer satisfaction by emailing codes directly
               to customers and enabling easy redemption through the POS system, with clear receipts and notifications
               "for a seamless experience.
                tus
                techultra
                techultra_private_limited_solution
                POS birthday reward
                Birthday loyalty program Odoo
                pos
                loyalty
                coupon
                birthday reward
                customer loyalty
                pos coupon
                promotion
                marketing
                discount
                rewards
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
                POS loyalty birthday reward
                POS birthday coupon system
                birthday reward coupon module
                POS customer birthday rewards
                automated birthday coupon generator
                POS loyalty reward system
                birthday discount coupon system
                POS coupon management system
                customer birthday promotion system
                POS loyalty program rewards
                coupon code generator system
                POS discount coupon management
                automated coupon code generation
                digital coupon management system
                POS coupon redemption system
                coupon reward automation
                customer discount coupon system
                POS promotional coupon system
                POS reward coupon generator
                coupon campaign management
                customer loyalty reward system
                POS customer engagement tools
                customer loyalty promotion system
                automated customer rewards
                POS loyalty marketing tools
                customer retention reward system
                loyalty rewards automation
                POS customer incentive system
                customer appreciation rewards
                loyalty program coupon system
                birthday promotion automation
                automated birthday discount system
                customer birthday reward automation
                birthday gift coupon system
                birthday marketing automation
                automated birthday email coupons
                birthday loyalty promotion
                birthday reward campaign system
                birthday celebration discount system
                customer birthday gift coupons
                retail POS reward system
                POS promotion management
                POS discount automation
                POS marketing automation tools
                POS customer reward management
                POS coupon distribution system
                POS promotional campaign tool
                retail loyalty reward automation
                POS customer reward notifications
                POS receipt coupon integration
                POS automated reward system
                POS customer reward tracking
                POS loyalty discount system
                POS promotional reward coupons
               """,
    "description": """ POS Loyalty birthday reward simplifies the process
                of generating, managing, and redeeming coupon codes in Odoo.
                It is designed to improve customer satisfaction and boost operational 
                efficiency by allowing businesses to send coupon codes directly to customers via email.
                The module also enables seamless redemption through the Point of Sale (POS) system.
                Detailed receipts and notifications ensure clarity and a smooth user experience.
                
                tus
                techultra
                techultra_private_limited_solution
                POS birthday reward
                Birthday loyalty program Odoo
                pos
                loyalty
                coupon
                birthday reward
                customer loyalty
                pos coupon
                promotion
                marketing
                discount
                rewards
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
                POS loyalty birthday reward
                POS birthday coupon system
                birthday reward coupon module
                POS customer birthday rewards
                automated birthday coupon generator
                POS loyalty reward system
                birthday discount coupon system
                POS coupon management system
                customer birthday promotion system
                POS loyalty program rewards
                coupon code generator system
                POS discount coupon management
                automated coupon code generation
                digital coupon management system
                POS coupon redemption system
                coupon reward automation
                customer discount coupon system
                POS promotional coupon system
                POS reward coupon generator
                coupon campaign management
                customer loyalty reward system
                POS customer engagement tools
                customer loyalty promotion system
                automated customer rewards
                POS loyalty marketing tools
                customer retention reward system
                loyalty rewards automation
                POS customer incentive system
                customer appreciation rewards
                loyalty program coupon system
                birthday promotion automation
                automated birthday discount system
                customer birthday reward automation
                birthday gift coupon system
                birthday marketing automation
                automated birthday email coupons
                birthday loyalty promotion
                birthday reward campaign system
                birthday celebration discount system
                customer birthday gift coupons
                retail POS reward system
                POS promotion management
                POS discount automation
                POS marketing automation tools
                POS customer reward management
                POS coupon distribution system
                POS promotional campaign tool
                retail loyalty reward automation
                POS customer reward notifications
                POS receipt coupon integration
                POS automated reward system
                POS customer reward tracking
                POS loyalty discount system
                POS promotional reward coupons
    """,
    'version': '19.0.0.0',
    "author": "TechUltra Solutions Private Limited",
    "company": "TechUltra Solutions Private Limited",
    "website": "https://www.techultrasolution.com",
    'category': 'Sales/Loyalty',
    "images": [
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
