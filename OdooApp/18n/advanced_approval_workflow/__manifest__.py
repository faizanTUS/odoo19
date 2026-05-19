# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Advanced Approval Workflow',
    'version': '18.0.0.0',
    'author': 'TechUltra Solutions Private Limited',
    'category': 'Operations',
    'website': 'https://www.techultrasolutions.com',
    "company": "TechUltra Solutions Private Limited",
    'summary': """
    Advanced approval management system enabling multi-level sequential workflows with automatic model-based approval triggers for purchase orders, sales orders, products, and custom business processes.
    odoo approval workflow
    multi-level approval system
    sequential approval process
    purchase order approval
    sales order approval workflow
    business process approval
    automated approval management
    approval automation software
    enterprise approval system
    workflow approval software
    configurable approval types
    required optional approvers
    domain-based approval rules
    model-based automatic approval
    approval tracking system
    approval status management
    approval notification system
    multi-step approval workflow
    approval hierarchy management
    document approval integration
    approval audit trail
    approval compliance tracking
    customizable approval chains
    approval workflow automation
    business approval controls
    purchase approval workflow
    invoice approval system
    product price approval
    financial approval process
    procurement approval software
    inventory approval management
    expense approval workflow
    contract approval system
    quotation approval process
    budget approval workflow
    HR approval management
    project approval system
    compliance approval software
    enterprise workflow automation
    business process automation
    Odoo18
    TUS
    tus
    techultra solutions
    techultra
    techultra solutions private limited
    """,
    'description': """
    Comprehensive approval solution featuring configurable approval types, required/optional approvers, domain-based activation rules, and seamless document integration. Supports unlimited approval levels with manager-based assignment and automated field synchronization. Perfect for controlling price changes, high-value transactions, and any business process requiring formal approval workflows.
    odoo approval workflow
    multi-level approval system
    sequential approval process
    purchase order approval
    sales order approval workflow
    business process approval
    automated approval management
    approval automation software
    enterprise approval system
    workflow approval software
    configurable approval types
    required optional approvers
    domain-based approval rules
    model-based automatic approval
    approval tracking system
    approval status management
    approval notification system
    multi-step approval workflow
    approval hierarchy management
    document approval integration
    approval audit trail
    approval compliance tracking
    customizable approval chains
    approval workflow automation
    business approval controls
    purchase approval workflow
    invoice approval system
    product price approval
    financial approval process
    procurement approval software
    inventory approval management
    expense approval workflow
    contract approval system
    quotation approval process
    budget approval workflow
    HR approval management
    project approval system
    compliance approval software
    enterprise workflow automation
    business process automation
    Odoo18
    TUS
    tus
    techultra solutions
    techultra
    techultra solutions private limited
    """,
    'depends': ['base', 'mail', 'product', 'hr'],
    'data': [
        'data/ir_sequence.xml',
        'data/mail_templates.xml',
        'security/approval_groups.xml',
        'security/approval_rules.xml',
        'security/ir.model.access.csv',
        'wizard/refused_reason_views.xml',
        'wizard/request_approval_views.xml',
        'wizard/rework_approval_views.xml',
        'wizard/cancel_approval_views.xml',
        'wizard/change_approver_views.xml',
        'views/approval_request_views.xml',
        'views/approval_type_views.xml',
        'views/approval_actions.xml',
        'views/approval_menus.xml',
    ],
    'images': [
        'static/description/main_screen.gif',
    ],
    'price': 22.00,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    "application": False,
}
