# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': 'Advanced Pricelist Prices on Product Form | Show & Hide Pricelist per Product & User',
    'version': '18.0.0.0',
    'category': 'Sales/Sales',
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'summary': """Show pricelist prices on product form and hide pricelists per product
    
    tus
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited
    Advanced Pricelist Prices on Product Form | Show & Hide Pricelist per Product & User
    Advanced Pricelist Prices on Product Form 
    Show & Hide Pricelist per Product & User
    pricelist
    product
    display pricelist prices
    pricelist on product form
    product pricelist price
    show pricelist price
    hide pricelist price
    advanced pricelist
    product pricing management
    multi pricelist display
    product price visibility
    user based price visibility
    pricelist price table
    product pricing control
    pricelist visibility control
    product price viewer
    pricing access control
    pricelist rules display
    product price comparison
    pricing transparency
    product pricing strategy
    sales price visibility
    product price management
    price list on product
    advanced pricing view
    internal pricing control
    product form pricing
    pricelist per product
    product pricing rules
    restricted pricing access
    pricing confidentiality
    business pricing tools
    product cost visibility
    sales pricing support
    price rule display
    pricing efficiency
    product price breakdown
    pricing administration
    product pricing overview
    advanced product pricing
    multi price list support
    pricing workflow improvement
    product price inspection
    price list management
    sales team pricing tool
    inventory pricing view
    product price audit
    pricing data security
    backend pricing tool
    enterprise pricing solution
    professional pricing module
    dynamic pricing visibility
    pricing rule overview
    controlled pricing display
    internal price reference
    product pricing analysis
    pricelist configuration tool
    pricing management extension
    pricing visibility rules
    advanced price display
    structured pricing view
    business price control
    product pricelist visibility
    pricelist price display module
    show multiple pricelists
    hide pricing per user
    product price access control
    pricing permission control
    pricelist on product page
    advanced pricelist management
    pricing rule visibility
    product pricing extension
    internal price reference tool
    backend pricelist display
    sales pricing transparency
    product pricing overview tool
    pricelist rule inspection
    price list viewer
    controlled price visibility
    multi pricing strategy
    product price comparison tool
    sales team pricing visibility
    product pricing intelligence
    pricing data governance
    advanced pricing interface
    pricing configuration assistant
    price rule auditing
    internal pricing dashboard
    pricing display enhancement
    product pricing reference
    advanced price control
    secure pricing visibility
    product price authorization
    pricing rule management
    pricelist pricing overvie
    pricing structure display
    pricing rule preview
    product pricing compliance
    advanced product price view
    pricing information security
    controlled pricelist access
    pricing visibility solution
    product price insight
    pricing decision support
    price visibility management
    product pricing governance
    pricing transparency tool
    advanced pricelist viewer
    product pricing supervision
    price control module
    product price monitoring
    internal pricing analysis
    product pricing workflow
    pricing rule visualization
    enterprise pricing control
    pricing access management
    product pricing support tool
    advanced pricing extension
    pricelist rule visibility control
    pricing overview per product
    backend product pricing
    secure pricelist display
    
    
    
    """,
    'description': """
Display Pricelist Price on Products (Advanced)
===============================================
- Display the product price according to different pricelists directly in the product form.
- **Pricelist level**: On each pricelist, use "Show on Product Form" to control whether that
  pricelist appears in the product table (when checked it can be shown, when unchecked it is
  never shown on any product form).
- **User level**: Each user has "Display Pricelist on Product" (Preferences / My Profile).
  When enabled, the pricelist section is visible on product forms; when disabled, the section
  is hidden for that user on all products.
- **Product level**: Hide all pricelist prices for a product, or hide specific pricelists from
  a product.

A table "Pricelist Price on The Product" shows Pricelist Name, Min Qty, Price, From Date, To Date.



    tus
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited
    Advanced Pricelist Prices on Product Form | Show & Hide Pricelist per Product & User
    Advanced Pricelist Prices on Product Form 
    Show & Hide Pricelist per Product & User
    pricelist
    product
    display pricelist prices
    pricelist on product form
    product pricelist price
    show pricelist price
    hide pricelist price
    advanced pricelist
    product pricing management
    multi pricelist display
    product price visibility
    user based price visibility
    pricelist price table
    product pricing control
    pricelist visibility control
    product price viewer
    pricing access control
    pricelist rules display
    product price comparison
    pricing transparency
    product pricing strategy
    sales price visibility
    product price management
    price list on product
    advanced pricing view
    internal pricing control
    product form pricing
    pricelist per product
    product pricing rules
    restricted pricing access
    pricing confidentiality
    business pricing tools
    product cost visibility
    sales pricing support
    price rule display
    pricing efficiency
    product price breakdown
    pricing administration
    product pricing overview
    advanced product pricing
    multi price list support
    pricing workflow improvement
    product price inspection
    price list management
    sales team pricing tool
    inventory pricing view
    product price audit
    pricing data security
    backend pricing tool
    enterprise pricing solution
    professional pricing module
    dynamic pricing visibility
    pricing rule overview
    controlled pricing display
    internal price reference
    product pricing analysis
    pricelist configuration tool
    pricing management extension
    pricing visibility rules
    advanced price display
    structured pricing view
    business price control
    product pricelist visibility
    pricelist price display module
    show multiple pricelists
    hide pricing per user
    product price access control
    pricing permission control
    pricelist on product page
    advanced pricelist management
    pricing rule visibility
    product pricing extension
    internal price reference tool
    backend pricelist display
    sales pricing transparency
    product pricing overview tool
    pricelist rule inspection
    price list viewer
    controlled price visibility
    multi pricing strategy
    product price comparison tool
    sales team pricing visibility
    product pricing intelligence
    pricing data governance
    advanced pricing interface
    pricing configuration assistant
    price rule auditing
    internal pricing dashboard
    pricing display enhancement
    product pricing reference
    advanced price control
    secure pricing visibility
    product price authorization
    pricing rule management
    pricelist pricing overvie
    pricing structure display
    pricing rule preview
    product pricing compliance
    advanced product price view
    pricing information security
    controlled pricelist access
    pricing visibility solution
    product price insight
    pricing decision support
    price visibility management
    product pricing governance
    pricing transparency tool
    advanced pricelist viewer
    product pricing supervision
    price control module
    product price monitoring
    internal pricing analysis
    product pricing workflow
    pricing rule visualization
    enterprise pricing control
    pricing access management
    product pricing support tool
    advanced pricing extension
    pricelist rule visibility control
    pricing overview per product
    backend product pricing
    secure pricelist display


    """,
    'depends': ['product', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_pricelist_views.xml',
        'views/res_users_views.xml',
        'views/product_template_views.xml',
    ],
    'images': [
        'static/description/main_screen.gif'
    ],
    'price': 12.00,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
