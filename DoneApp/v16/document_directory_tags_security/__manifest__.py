# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
{
    "name": "Document Access & Directory Hub | Directory-Based Document Manager | Document Control & Directory System | Centralized Document Directory",
    "version": "16.0.0.0",
    "category": "Productivity/Documents",
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    "summary": """
    Organize business documents through structured parent and child directories, creating a scalable and efficient document management system.
    document management system
    document directory management
    file organization system
    digital document storage
    document access control
    document security management
    directory-based file management
    hierarchical document structure
    document categorization system
    file tagging system
    document workflow organization
    centralized document repository
    business document management
    enterprise document system
    document sharing control
    secure file management
    document visibility control
    user-based document access
    role-based file permissions
    document indexing system    
    document classification tools
    smart document organization
    document storage solution
    file directory structure
    document archive management
    document tracking system
    document lifecycle management
    document collaboration system
    internal document management
    multi-user document system
    structured file storage
    directory security system
    document tagging solution
    document control system
    digital file organization
    document access system
    cloud-ready document management
    business file organization
    document system for companies
     """,

    "description": """
    This module enhances Odoo&apos;s document management capabilities by providing a structured directory-based system for organizing and controlling business documents. The module enables users to manage files through hierarchical parent and child directories, creating a clear and scalable document organization framework.
    document management system
    document directory management
    file organization system
    digital document storage
    document access control
    document security management
    directory-based file management
    hierarchical document structure
    document categorization system
    file tagging system
    document workflow organization
    centralized document repository
    business document management
    enterprise document system
    document sharing control
    secure file management
    document visibility control
    user-based document access
    role-based file permissions
    document indexing system
    document classification tools
    smart document organization
    document storage solution
    file directory structure
    document archive management
    document tracking system
    document lifecycle management
    document collaboration system
    internal document management
    multi-user document system
    structured file storage
    directory security system
    document tagging solution
    document control system
    digital file organization
    document access system
    cloud-ready document management
    business file organization
    document system for companies
    """,
    "depends": ["base", "web", "mail"],
    "data": [
        "security/document_hub_security.xml",
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "data/ir_sequence_data.xml",
        "views/document_directory_tag_views.xml",
        "views/document_tag_views.xml",
        "views/document_directory_views.xml",
        "views/ir_attachment_views.xml",
        "views/menu.xml",
    ],
    'images': [
        'static/description/main_screen.gif'
    ],
    'price': 24.95,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    "post_init_hook": "post_init_hook",
}
