# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
{
    'name': 'Material Requisition Management | Purchase & Inventory Workflow | Multi-Level Approval',
    'version': '16.0.0.0',
    'category': 'Inventory/Inventory',
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'summary': """
    Efficiently manage material requests, approvals, and fulfillment with a complete workflow-driven system integrated with procurement and inventory operations.
    
    tus
    techultra
    techultra_private_limited_solution
    picking
    purchase
    Material Requisition
    purchase approval workflow
    picking approval workflow
    material requisition system
    material request management
    material requisition workflow
    material request approval system
    internal material request process
    inventory request system
    stock request management
    purchase requisition system
    purchase request workflow
    procurement request management
    material requisition automation
    inventory requisition management
    material demand management
    internal procurement workflow
    request to purchase process
    material issue request system
    warehouse request system
    stock movement request management
    inventory request automation
    requisition approval workflow
    material request software
    requisition management solution
    purchase requisition automation
    internal stock request system
    material requisition tracking
    inventory control management
    warehouse inventory request system
    procurement workflow solution
    material request tracking system
    stock request approval system
    material requisition with approval workflow
    purchase and inventory integration system
    stock transfer request management
    internal stock transfer workflow
    inventory movement management
    material planning solution
    procurement management system
    request management workflow
    approval workflow system
    business process automation
    material requisition enterprise solution
    inventory workflow management
    purchase workflow system
    stock control management
    internal operations workflow
    requisition tracking system
    inventory operations management
    warehouse process management
    material handling workflow
    procurement lifecycle system
    request approval system
    internal request workflow system
    purchase integration workflow
    stock request tracking system
    inventory request lifecycle management
    automated requisition workflow
    business workflow system
    enterprise inventory management solution
    material supply request system
    internal logistics workflow
    multi-level approval workflow
    approval management system
    workflow automation solution
    inventory request processing system
    purchase order workflow automation
    stock movement control system
    internal supply chain workflow
    requisition process management
    inventory planning system
    material request control system
    real-time requisition tracking
    request status tracking system
    inventory visibility solution
    audit trail workflow system
    internal communication tracking system
    request lifecycle workflow
    automated approval system
    smart requisition management system
    
    """,
    'description': """
Material Requisition & Inventory Management with Purchase Workflow
===============================================
Material Purchase Requisitions and Internal Picking Requisitions by Employee / User.

This app enables employees to create material requisition requests. Requests undergo department manager
and requisition officer approval. Supports:
- Employee requests with multiple lines; employees see only their own records.
- Department manager approve/decline.
- Requisition officer approve/reject; set destination location; add vendor per line; generate pickings/POs.
- Per-line action: Purchase Order (RFQ to vendor) or Internal Picking (internal transfer).
- Email notifications for approval requests.
- User default stock location (requisitions placed from configured location per user).
- PDF report and Received button for employees.


    tus
    techultra
    techultra_private_limited_solution
    picking
    purchase
    Material Requisition
    purchase approval workflow
    picking approval workflow
    material requisition system
    material request management
    material requisition workflow
    material request approval system
    internal material request process
    inventory request system
    stock request management
    purchase requisition system
    purchase request workflow
    procurement request management
    material requisition automation
    inventory requisition management
    material demand management
    internal procurement workflow
    request to purchase process
    material issue request system
    warehouse request system
    stock movement request management
    inventory request automation
    requisition approval workflow
    material request software
    requisition management solution
    purchase requisition automation
    internal stock request system
    material requisition tracking
    inventory control management
    warehouse inventory request system
    procurement workflow solution
    material request tracking system
    stock request approval system
    material requisition with approval workflow
    purchase and inventory integration system
    stock transfer request management
    internal stock transfer workflow
    inventory movement management
    material planning solution
    procurement management system
    request management workflow
    approval workflow system
    business process automation
    material requisition enterprise solution
    inventory workflow management
    purchase workflow system
    stock control management
    internal operations workflow
    requisition tracking system
    inventory operations management
    warehouse process management
    material handling workflow
    procurement lifecycle system
    request approval system
    internal request workflow system
    purchase integration workflow
    stock request tracking system
    inventory request lifecycle management
    automated requisition workflow
    business workflow system
    enterprise inventory management solution
    material supply request system
    internal logistics workflow
    multi-level approval workflow
    approval management system
    workflow automation solution
    inventory request processing system
    purchase order workflow automation
    stock movement control system
    internal supply chain workflow
    requisition process management
    inventory planning system
    material request control system
    real-time requisition tracking
    request status tracking system
    inventory visibility solution
    audit trail workflow system
    internal communication tracking system
    request lifecycle workflow
    automated approval system
    smart requisition management system
    
    """,
    'depends': [
        'base',
        'mail',
        'product',
        'stock',
        'purchase',
        'hr',
    ],
    'data': [
        'security/material_requisition_groups.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/material_requisition_config_data.xml',
        'data/mail_templates.xml',
        'wizard/material_requisition_reject_wizard_views.xml',
        'report/material_requisition_report_templates.xml',
        'report/material_requisition_report.xml',
        'views/material_requisition_views.xml',
        'views/material_requisition_config_views.xml',
        'views/res_users_views.xml',
        'views/material_requisition_menus.xml',
    ],
    'images': [
        'static/description/main_screen.gif'
    ],
    'price': 35.00,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
