# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
{
    "name": "Document Access & Directory Hub | Directory-Based Document Manager | Document Control & Directory System | Centralized Document Directory",
    "version": "17.0.0.0",
    "category": "Productivity/Documents",
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    "summary": """
    The Document Directory Hub module enables structured and secure document management through a hierarchical directory system.It allows users to organize files using directories, sub-directories, and tags. With role-based access control, users can only view documents assigned to them.Dedicated menus like All Documents and My Documents improve accessibility and user experience.
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
    The Document Directory Hub module provides a centralized platform to efficiently manage and organize documents.Users can create directories with parent-child relationships and categorize them using customizable tags with color coding.It supports advanced configuration options such as sequences, related models, and company-specific settings.The module ensures strong security by allowing directory-level access control through users and groups.Personalized and global document views help users quickly access relevant files.Overall, it enhances document organization, security, and usability for businesses of all sizes.
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
