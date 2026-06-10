# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Advanced Approval Workflow for Odoo | Odoo Multi-Level Approval Workflow | Dynamic Approval Management for Odoo',
    'version': '17.0.0.0',
    'author': 'TechUltra Solutions Private Limited',
    'category': 'Operations',
    'website': 'https://www.techultrasolutions.com',
    "company": "TechUltra Solutions Private Limited",
    'summary': """
    Advanced Approval Workflow for Odoo enables businesses to manage approval processes with configurable approval rules, multi-level approvals, and automated approver assignments. It helps ensure better control, compliance, and transparency across critical business operations
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
    Advanced Approval Workflow for Odoo is a flexible approval management solution designed to streamline business processes that require authorization and control. The module supports configurable approval types, multi-level approval workflows, required and optional approvers, and domain-based approval rules. Users can approve, reject, and track requests with complete visibility and audit history. It helps organizations improve compliance, reduce manual oversight, and ensure proper approval procedures across critical business operations.
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
    'price': 21.81,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    "application": False,
}
