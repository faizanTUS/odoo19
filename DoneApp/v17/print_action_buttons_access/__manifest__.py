# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
{
    "name": "Print & Action Buttons Access | Restrict Report and Action Menu by User Groups",
    "version": "17.0.0.0",
    "category": "Tools",
    'author': "TechUltra Solutions Private Limited",
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    "summary": """
    This module restricts access to Odoo Print and Action buttons by checking user group permissions and dynamically hiding them in the web interface.


        tus
        techultra
        techultra_private_limited_solution
        Print & Action Buttons Access | Restrict Report and Action Menu by User Groups
        Print & Action Buttons Access 
        Restrict Report and Action Menu by User Groups
        print button access control
        access control module
        restrict print button
        action menu permission control
        print button restriction
        action menu restriction
        report access control
        report permission management
        user role permissions
        group based access control
        action button visibility control
        report security management
        interface permission control
        role based system security
        secure report generation
        action execution control
        user access restriction
        menu visibility management
        report generation restriction
        group based access control
        action button access control
        report access restriction
        user permission management
        access control module
        role based access control
        group based permissions
        advanced access restriction
        system permission management
        user access security
        hide print button
        restrict print button access
        print menu visibility control
        report printing restriction
        print permission control
        report generation restriction
        print access management
        report visibility control
        print action security
        report printing access control
        hide action menu
        restrict action button
        action menu permission control
        server action restriction
        action execution security
        action menu visibility control
        restrict system actions
        action button permissions
        action operation restriction
        action workflow control
        enterprise access control
        advanced security module
        permission restriction tool
        user role security
        enterprise permission control
        workflow security control
        role permission manager
        secure system operations
        enterprise security extension
        permission visibility control
        secure business workflow
        report protection system
        sensitive report restriction
        workflow access restriction
        business data protection
        operational access security
        enterprise workflow protection
        system operation control
        business report security
        controlled user operations
        hide interface buttons
        dynamic button visibility control
        interface access restriction
        menu visibility security
        UI permission control
        secure action execution
        controlled report generation
        restricted system operations
        advanced role permissions
        secure interface access
    """,
    "description": """
        Control the visibility of Print and Action buttons in Odoo using user group permissions. Improve security by 
        restricting report generation and server actions to authorized users only.


        tus
        techultra
        techultra_private_limited_solution
        Print & Action Buttons Access | Restrict Report and Action Menu by User Groups
        Print & Action Buttons Access 
        Restrict Report and Action Menu by User Groups
        print button access control
        access control module
        restrict print button
        action menu permission control
        print button restriction
        action menu restriction
        report access control
        report permission management
        user role permissions
        group based access control
        action button visibility control
        report security management
        interface permission control
        role based system security
        secure report generation
        action execution control
        user access restriction
        menu visibility management
        report generation restriction
        group based access control
        action button access control
        report access restriction
        user permission management
        access control module
        role based access control
        group based permissions
        advanced access restriction
        system permission management
        user access security
        hide print button
        restrict print button access
        print menu visibility control
        report printing restriction
        print permission control
        report generation restriction
        print access management
        report visibility control
        print action security
        report printing access control
        hide action menu
        restrict action button
        action menu permission control
        server action restriction
        action execution security
        action menu visibility control
        restrict system actions
        action button permissions
        action operation restriction
        action workflow control
        enterprise access control
        advanced security module
        permission restriction tool
        user role security
        enterprise permission control
        workflow security control
        role permission manager
        secure system operations
        enterprise security extension
        permission visibility control
        secure business workflow
        report protection system
        sensitive report restriction
        workflow access restriction
        business data protection
        operational access security
        enterprise workflow protection
        system operation control
        business report security
        controlled user operations
        hide interface buttons
        dynamic button visibility control
        interface access restriction
        menu visibility security
        UI permission control
        secure action execution
        controlled report generation
        restricted system operations
        advanced role permissions
        secure interface access
    """,
    "depends": ["web", "base"],
    "data": [
        "security/security.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "print_action_buttons_access/static/src/action_menus/action_menus_patch.js",
            "print_action_buttons_access/static/src/cog_menu/cog_menu_patch.js",
        ],
    },
    "images": [
        "static/description/main_screen.gif",
    ],
    'currency': 'USD',
    'price': 10.00,
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}