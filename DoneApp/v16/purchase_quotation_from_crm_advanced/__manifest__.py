# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': 'CRM to Purchase Quotation Advanced | Generate RFQ from Leads & Opportunities',
    'version': '16.0.0.0',
    'category': 'Sales/Purchase/CRM',
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'summary': """Create and manage Purchase Quotations from CRM Leads with configuration and advanced features

    tus
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited
    CRM Purchase
    purchase
    crm
    purchase crm
    quotation
    RFQ
    lead
    Opportunity
    CRM to Purchase Quotation Advanced | Generate RFQ from Leads & Opportunities
    CRM to Purchase Quotation Advanced
    Generate RFQ from CRM Leads
    CRM to Purchase Integration
    Generate RFQ from CRM
    RFQ from Lead
    RFQ from Opportunity
    Create Purchase Quotation from CRM
    CRM Purchase Workflow
    Lead to RFQ Automation
    Opportunity to Purchase Quotation
    CRM Procurement Integration
    Purchase Request from CRM
    Vendor Quotation from Lead
    Automated RFQ Creation
    Procurement from Opportunity
    Purchase Workflow Automation
    Sales to Purchase Integration
    Lead Based Procurement
    Smart RFQ Generation
    Vendor Quotation Management
    Purchase Request Automation
    Procurement Process Optimization
    Seamless CRM Purchase Workflow
    Cross Department Workflow Integration
    CRM to Vendor Quotation
    Sales Procurement Coordination
    Lead Linked RFQ
    Document Traceability CRM
    Opportunity Based Procurement
    Business Process Automation
    Procurement Tracking from CRM
    Integrated Sales and Purchase
    Vendor Selection Wizard
    Automatic Product Transfer RFQ
    RFQ Smart Button CRM
    CRM Linked Purchase Order
    Lead Product to RFQ
    Vendor Creation from CRM
    Multi RFQ from Lead
    Opportunity Procurement Tracking
    Purchase Quotation Wizard
    Lead to Vendor Workflow
    Advanced CRM RFQ Management
    Enterprise Procurement Integration
    Structured RFQ Workflow
    CRM Based Vendor Management
    Purchase Quotation Automation
    CRM Driven Procurement
    Procurement Workflow Enhancement
    Opportunity Linked Purchase Documents
    Vendor RFQ from Opportunity
    Business Workflow Integration Tool
    CRM Purchase Connector
    Lead to Purchase Module
    Opportunity to RFQ Module
    Procurement Integration Addon
    CRM RFQ Automation Tool
    Vendor Quotation Integration Module
    Purchase Automation Extension
    CRM Procurement Addon
    RFQ Generation Module
    Lead Based Purchase Extension
    CRM to Vendor Integration
    Instant RFQ from Lead
    Opportunity Purchase Automation
    Lead Driven Procurement
    Pre-Sales Vendor Quotation
    CRM Based Purchase Initiation
    Lead to Procurement Process
    Opportunity Vendor RFQ
    Integrated RFQ Management
    Purchase Quotation from Opportunity
    Sales Opportunity to RFQ
    CRM Triggered Purchase Workflow
    Vendor RFQ Automation
    Lead Linked Vendor Quotation
    Procurement Initiation from CRM
    CRM Purchase Synchronization
    Opportunity to Vendor Management
    Purchase Quotation Creation Tool
    CRM Purchase Process Optimization
    Smart Procurement from Lead
    """,
    'description': """
CRM to Purchase Quotation Advanced | Generate RFQ from Leads & Opportunities
=======================================
* Create Purchase Quotation directly from CRM Leads (New Purchase Quotation button).
* Stay in CRM workflow while initiating and managing RFQs.
* Choose: create new vendor or link to existing vendor (wizard like Sale CRM).
* Pre-fill RFQ lines from lead requested products (optional).
* Automatically link each RFQ/PO to originating Lead; view from Lead via smart buttons.
* Configurable defaults and behavior via Settings.
* Control access via standard CRM and Purchase roles.


    tus
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited
    CRM Purchase
    purchase
    crm
    purchase crm
    quotation
    RFQ
    lead
    Opportunity
    CRM to Purchase Quotation Advanced | Generate RFQ from Leads & Opportunities
    CRM to Purchase Quotation Advanced
    Generate RFQ from CRM Leads
    CRM to Purchase Integration
    Generate RFQ from CRM
    RFQ from Lead
    RFQ from Opportunity
    Create Purchase Quotation from CRM
    CRM Purchase Workflow
    Lead to RFQ Automation
    Opportunity to Purchase Quotation
    CRM Procurement Integration
    Purchase Request from CRM
    Vendor Quotation from Lead
    Automated RFQ Creation
    Procurement from Opportunity
    Purchase Workflow Automation
    Sales to Purchase Integration
    Lead Based Procurement
    Smart RFQ Generation
    Vendor Quotation Management
    Purchase Request Automation
    Procurement Process Optimization
    Seamless CRM Purchase Workflow
    Cross Department Workflow Integration
    CRM to Vendor Quotation
    Sales Procurement Coordination
    Lead Linked RFQ
    Document Traceability CRM
    Opportunity Based Procurement
    Business Process Automation
    Procurement Tracking from CRM
    Integrated Sales and Purchase
    Vendor Selection Wizard
    Automatic Product Transfer RFQ
    RFQ Smart Button CRM
    CRM Linked Purchase Order
    Lead Product to RFQ
    Vendor Creation from CRM
    Multi RFQ from Lead
    Opportunity Procurement Tracking
    Purchase Quotation Wizard
    Lead to Vendor Workflow
    Advanced CRM RFQ Management
    Enterprise Procurement Integration
    Structured RFQ Workflow
    CRM Based Vendor Management
    Purchase Quotation Automation
    CRM Driven Procurement
    Procurement Workflow Enhancement
    Opportunity Linked Purchase Documents
    Vendor RFQ from Opportunity
    Business Workflow Integration Tool
    CRM Purchase Connector
    Lead to Purchase Module
    Opportunity to RFQ Module
    Procurement Integration Addon
    CRM RFQ Automation Tool
    Vendor Quotation Integration Module
    Purchase Automation Extension
    CRM Procurement Addon
    RFQ Generation Module
    Lead Based Purchase Extension
    CRM to Vendor Integration
    Instant RFQ from Lead
    Opportunity Purchase Automation
    Lead Driven Procurement
    Pre-Sales Vendor Quotation
    CRM Based Purchase Initiation
    Lead to Procurement Process
    Opportunity Vendor RFQ
    Integrated RFQ Management
    Purchase Quotation from Opportunity
    Sales Opportunity to RFQ
    CRM Triggered Purchase Workflow
    Vendor RFQ Automation
    Lead Linked Vendor Quotation
    Procurement Initiation from CRM
    CRM Purchase Synchronization
    Opportunity to Vendor Management
    Purchase Quotation Creation Tool
    CRM Purchase Process Optimization
    Smart Procurement from Lead


    """,
    'depends': ['crm', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/crm_lead_views.xml',
        'views/purchase_order_views.xml',
        'wizard/crm_lead_purchase_quotation_wizard_views.xml',
    ],
    'images': [
        'static/description/main_screen.gif'
    ],
    'currency': 'USD',
    'price': 12.00,
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
