# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'TUS Removed Powered By Odoo',
    "author": "TechUltra Solutions Private Limited",
    "company": "TechUltra Solutions Private Limited",
    "website": "https://www.techultrasolution.com",
    'category': 'Odoo Branding',
    'version': '19.0.0.0',
    'summary': """
        Removes all "Powered by Odoo" references from Website, Portal, Survey, POS, and 
        Email Templates — providing a fully white-labeled experience without modifying Odoo core files.

        tus 
        TUS
        TechUltra Solutions Private Limited
        techUltra solutions private limited
        odoo 14
        odoo 15
        odoo 16
        odoo 17
        odoo 18
        odoo 19
        remove powered by odoo
        odoo branding removal
        odoo white label
        hide powered by odoo
        odoo website footer remove
        odoo portal footer remove
        odoo survey branding
        odoo pos branding
        odoo email footer remove
        odoo rebranding module
        remove branding
        odoo footer remove
        hide powered by odoo
        odoo website branding
        odoo portal branding
        odoo email footer
        odoo rebrand module
        odoo customization
        odoo clean footer
        odoo remove copyright
        odoo remove powered by odoo
        odoo remove footer branding
        odoo remove default footer
        odoo hide powered by odoo text
        odoo branding removal module
        odoo white label branding
        odoo custom branding module
        odoo rebranding module
        odoo no powered by odoo
        odoo remove portal footer
        odoo remove survey footer
        odoo remove website footer
        odoo remove email footer
        odoo remove pos branding
        odoo remove copyright footer
        odoo website customization
        odoo professional branding
        odoo client branding
        odoo clean layout
        odoo rebrand odoo frontend
        odoo remove default branding
        odoo footer customization
        odoo remove logo and text


        """
    ,
    'description': """
     This module completely removes the "Powered by Odoo" text from:
        - Website footers
        - Customer Portal pages
        - Survey 
        - Point of Sale receipts
        - Standard email templates
        
        It provides a professional, fully white-labeled experience while keeping your Odoo core clean.    
        Perfect for businesses, implementers, and resellers who want to present Odoo as their own solution.
    
        tus 
        TUS
        TechUltra Solutions Private Limited
        techUltra solutions private limited
        odoo 14
        odoo 15
        odoo 16
        odoo 17
        odoo 18
        odoo 19
        remove powered by odoo
        odoo branding removal
        odoo white label
        hide powered by odoo
        odoo website footer remove
        odoo portal footer remove
        odoo survey branding
        odoo pos branding
        odoo email footer remove
        odoo rebranding module
        remove branding
        odoo footer remove
        hide powered by odoo
        odoo website branding
        odoo portal branding
        odoo email footer
        odoo rebrand module
        odoo customization
        odoo clean footer
        odoo remove copyright
        odoo remove powered by odoo
        odoo remove footer branding
        odoo remove default footer
        odoo hide powered by odoo text
        odoo branding removal module
        odoo white label branding
        odoo custom branding module
        odoo rebranding module
        odoo no powered by odoo
        odoo remove portal footer
        odoo remove survey footer
        odoo remove website footer
        odoo remove email footer
        odoo remove pos branding
        odoo remove copyright footer
        odoo website customization
        odoo professional branding
        odoo client branding
        odoo clean layout
        odoo rebrand odoo frontend
        odoo remove default branding
        odoo footer customization
        odoo remove logo and text

    """,
    'depends': ['web','survey','mail','portal'],
    'data': [
        'views/web_remove_powered_by_odoo.xml',
        'views/survey_templates_inherit.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'tus_remove_powered_by_odoo/static/src/scss/website.scss',
        ],
        'point_of_sale._assets_pos': [
            'tus_remove_powered_by_odoo/static/src/xml/order_receipt.xml',
        ],
    },
    "images": [
        "static/description/main_screen.gif",
    ],
    'installable': True,
    'auto_install': False,
    "license": "OPL-1",
}