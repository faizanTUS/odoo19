# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    "name": "Tally Style Indian Accounting & P&L Reporting for Odoo",
    "version": "18.0.0.0",
    "category": "Accounting",
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com",
    "summary": """
        Bring familiar Tally-style Profit & Loss, opening/closing stock, and Anglo-Saxon inventory accounting into Odoo for Indian companies.
            
        tus
        TUS
        TechUltra Solutions Private Limited
        techUltra solutions private limited
        TechUltra Solutions
        stock account 
        stock tally Odoo
        india stock
        india tally
        tally
        Tally type reporting Odoo 
        Odoo Tally reporting
        Tally style P&L Odoo
        Odoo Indian accounting
        Odoo India localization
        Tally wise reporting Odoo
        Anglo Saxon accounting Tally Odoo
        Opening stock closing stock Odoo
        Odoo Profit and Loss India
        migrate from Tally to Odoo
        Odoo perpetual inventory India
        Odoo stock valuation Indian chart
        Odoo COGS Tally method
        Indian manufacturer accounting Odoo
        distributor ERP India Odoo
        CA friendly Odoo reports India
        Odoo Enterprise accounting India
        GST Odoo inventory accounting
        TechUltra Odoo India module
            """,
    "description": """
        Tally-style Indian Profit & Loss reporting in Odoo with Opening Stock, Closing Stock, Gross Profit, and Anglo-Saxon accounting aligned 
        to Tally-plus automated perpetual inventory setup for India.
        
        
        tus
        TUS
        TechUltra Solutions Private Limited
        techUltra solutions private limited
        TechUltra Solutions
        stock account 
        stock tally Odoo
        india stock
        india tally
        tally
        Tally type reporting Odoo 
        Odoo Tally reporting
        Tally style P&L Odoo
        Odoo Indian accounting
        Odoo India localization
        Tally wise reporting Odoo
        Anglo Saxon accounting Tally Odoo
        Opening stock closing stock Odoo
        Odoo Profit and Loss India
        migrate from Tally to Odoo
        Odoo perpetual inventory India
        Odoo stock valuation Indian chart
        Odoo COGS Tally method
        Indian manufacturer accounting Odoo
        distributor ERP India Odoo
        CA friendly Odoo reports India
        Odoo Enterprise accounting India
        GST Odoo inventory accounting
        TechUltra Odoo India module
        
    """,
    "depends": [
        'stock_account',
        'account_reports',
        'l10n_in_reports',
        'l10n_in',
        'account',
    ],
    "data": [
        'views/res_config_settings_views.xml',
    ],
    "post_init_hook": "post_init_hook",
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 99.90,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    'application': False,
}
