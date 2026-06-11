# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': 'Odoo Portal Quotation Editor | Edit Quantity & Delete Sale Order Lines',
    'version': '18.0.0.0',
    'author': 'Techultra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'category': 'Sales',
    'summary': """ Allow portal users to edit quantities and delete lines on quotations
    
        tus
        techultra
        techultra_private_limited_solution
        portal
        portal users
        portal customize
        portal edit
        portal quotation edit
        Quotation editing module
        Portal quotation management
        Customize quotation lines
        Edit quotation lines
        Delete quotation lines
        Dynamic quotation customize
        Dynamic quotation editing
        Quotation modification module
        Sales order quotation updates
        Real-time quotation updates
        Online quotation customize
        Online quotation editing
        Edit and delete quotation lines
        Sales quotation portal
        Customer portal quotation management
        Quotation line management
        Real-time sales quotation updates
        Modify quotation quantities
        Modify quotations online
        Automated quotation synchronization
        Product quantity update in quotations
        Quotation customization module
        Quote editing and deletion for portal users
        Sales process automation
        Order management system (OMS)
        Customer portal functionality
        ERP quotation management
        Sales and quotation automation software
        B2B quotation portal system
        Customer self-service portal for quotations
        Portal quotation editor
        Edit quotations online
        Delete quotation lines portal
        Quotation line management software
        Real-time quote editing
        Quotation quantity updater
        Customer portal quotation module
        Online quotation modification
        Quotation management system
        Sales quotation editor
        Edit and delete lines in quotation
        Update product quantity in quotation
        Portal quotation updates for customers
        Backend synchronized quotations
        Quotation editing for sales orders
        Online sales quotation editing tool
        Editable quotation lines for portal users
        Quote management portal module
        Quotation adjustment portal tool
        Modify quotation before confirmation
        B2B portal quotation editor
        Manufacturing sales quotation management
        Wholesale customer portal quotations
        Online quotation editing for distributors
        Quotation line management for service businesses
        Retail portal quote modification
        Multi-currency portal quotation editor
        International sales quotation tool
        Editable quotes for e-commerce B2B portals
        Quotation editing for enterprise portals
        
    """,
    'description': """
        This module allows portal users to:
        - Edit product quantities on quotation lines
        - Delete order lines from quotations
        Changes are reflected in the backend sale order.
        
        
        tus
        techultra
        techultra_private_limited_solution
        portal
        portal users
        portal customize
        portal edit
        portal quotation edit
        Quotation editing module
        Portal quotation management
        Customize quotation lines
        Edit quotation lines
        Delete quotation lines
        Dynamic quotation customize
        Dynamic quotation editing
        Quotation modification module
        Sales order quotation updates
        Real-time quotation updates
        Online quotation customize
        Online quotation editing
        Edit and delete quotation lines
        Sales quotation portal
        Customer portal quotation management
        Quotation line management
        Real-time sales quotation updates
        Modify quotation quantities
        Modify quotations online
        Automated quotation synchronization
        Product quantity update in quotations
        Quotation customization module
        Quote editing and deletion for portal users
        Sales process automation
        Order management system (OMS)
        Customer portal functionality
        ERP quotation management
        Sales and quotation automation software
        B2B quotation portal system
        Customer self-service portal for quotations
        Portal quotation editor
        Edit quotations online
        Delete quotation lines portal
        Quotation line management software
        Real-time quote editing
        Quotation quantity updater
        Customer portal quotation module
        Online quotation modification
        Quotation management system
        Sales quotation editor
        Edit and delete lines in quotation
        Update product quantity in quotation
        Portal quotation updates for customers
        Backend synchronized quotations
        Quotation editing for sales orders
        Online sales quotation editing tool
        Editable quotation lines for portal users
        Quote management portal module
        Quotation adjustment portal tool
        Modify quotation before confirmation
        B2B portal quotation editor
        Manufacturing sales quotation management
        Wholesale customer portal quotations
        Online quotation editing for distributors
        Quotation line management for service businesses
        Retail portal quote modification
        Multi-currency portal quotation editor
        International sales quotation tool
        Editable quotes for e-commerce B2B portals
        Quotation editing for enterprise portals
        
    """,
    'depends': ['sale', 'portal', 'website_sale'],
    'data': [
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'portal_quotation_customize/static/src/js/portal_quotation.js',
        ],
    },
    "images": [
        "static/description/main_screen.gif",
    ],
    'currency': 'USD',
    'price': 16.00,
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}
