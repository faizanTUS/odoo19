# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    "name": "Smart Ageing Alerts for Customers & Vendors | Invoice Due Alerts, Overdue Bills & Payment Risk Monitoring",
    "version": "17.0.0.0",
    "category": "Accounting",
    "summary": """
    Ageing alerts for customer invoices and vendor bills
    
    tus
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited
    ageing alerts 
    overdue alerts 
    customer ageing
    vendor ageing
    invoice overdue
    bill overdue
    credit control
    payable monitoring
    receivable monitoring
    finance automation
    accounting alerts
    due date alerts
    partner ageing
    odoo ageing
    credit risk
    vendor bills
    customer invoices
    activity alerts
    ageing alerts
    overdue alerts
    customer ageing
    vendor ageing
    invoice overdue
    bill overdue
    credit control
    payable monitoring
    receivable monitoring
    finance automation
    accounting alerts
    due date alerts
    partner ageing
    odoo ageing
    credit risk
    vendor bills
    customer invoices
    activity alerts
    due alerts
    financial alerts
    invoice control
    bill control
    debt control
    overdue partner
    automated reminders
    partner balance alerts
    account move alerts
    overdue management
    credit team tools
    finance workflow
    overdue detection
    receivable alerts
    payable alerts
    account analysis
    partner notifications
    business finance tools
    overdue tracking
    late payment alerts
    overdue summary
    ageing automation
    partner follow-up
    finance intelligence
    alert scheduler
    cron alerts
    odoo accounting enhancement
    overdue compliance
    vendor due alerts
    customer due alerts
    partner monitoring
    invoice deadline alerts
    bill deadline alerts
    risk partner alerts
    financial workflow automation
    alert system
    alert engine
    accounting extension
    partner priority alerts
    payment overdue
    due balance alerts
    partner credit alerts
    partner payable risk
    partner receivable risk
    late invoice alerts
    late bill alerts
    finance control
    financial risk alerts
    debt monitoring
    partner due summary
    delinquent account alerts
    credit exposure alerts
    vendor balance alerts
    customer balance alerts
    aging dashboard
    aging intelligence
    alert automation
    financial oversight
    credit monitoring
    payment risk alerts
    account follow-up
    debt follow-up
    receivable control
    payable control
    finance reminders
    due invoice list
    due bill list
    statement overdue
    partner health score
    account risk score
    risk partner detection
    critical overdue alerts
    high priority alerts
    medium priority alerts
    low priority alerts
    finance escalation
    overdue escalation
    payment priority alerts
    account priority levels
    credit decision support
    financial workflow control
    internal finance tools
    partner debt summary
    late payment detection
    aging analytics
    partner overdue analytics
    payment timeline alerts
    priority-based alerts
    partner financial status
    invoice tracking
    bill tracking
    due account tracking
    aging summary alerts

    
    """,
    "description": """
    This module adds automated ageing alerts for overdue customer invoices and vendor bills. It checks each partner’s 
    receivable and payable balances, detects overdue amounts above your configured threshold, and creates clear activity 
    alerts on the partner. The system applies a cooldown period to limit alerts to one per partner per day and prevents 
    multiple message. You can enable customer alerts, vendor alerts, or both.

    
    
    tus
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited
    ageing alerts 
    overdue alerts 
    customer ageing
    vendor ageing
    invoice overdue
    bill overdue
    credit control
    payable monitoring
    receivable monitoring
    finance automation
    accounting alerts
    due date alerts
    partner ageing
    odoo ageing
    credit risk
    vendor bills
    customer invoices
    activity alerts
    ageing alerts
    overdue alerts
    customer ageing
    vendor ageing
    invoice overdue
    bill overdue
    credit control
    payable monitoring
    receivable monitoring
    finance automation
    accounting alerts
    due date alerts
    partner ageing
    odoo ageing
    credit risk
    vendor bills
    customer invoices
    activity alerts
    due alerts
    financial alerts
    invoice control
    bill control
    debt control
    overdue partner
    automated reminders
    partner balance alerts
    account move alerts
    overdue management
    credit team tools
    finance workflow
    overdue detection
    receivable alerts
    payable alerts
    account analysis
    partner notifications
    business finance tools
    overdue tracking
    late payment alerts
    overdue summary
    ageing automation
    partner follow-up
    finance intelligence
    alert scheduler
    cron alerts
    odoo accounting enhancement
    overdue compliance
    vendor due alerts
    customer due alerts
    partner monitoring
    invoice deadline alerts
    bill deadline alerts
    risk partner alerts
    financial workflow automation
    alert system
    alert engine
    accounting extension
    partner priority alerts
    payment overdue
    due balance alerts
    partner credit alerts
    partner payable risk
    partner receivable risk
    late invoice alerts
    late bill alerts
    finance control
    financial risk alerts
    debt monitoring
    partner due summary
    delinquent account alerts
    credit exposure alerts
    vendor balance alerts
    customer balance alerts
    aging dashboard
    aging intelligence
    alert automation
    financial oversight
    credit monitoring
    payment risk alerts
    account follow-up
    debt follow-up
    receivable control
    payable control
    finance reminders
    due invoice list
    due bill list
    statement overdue
    partner health score
    account risk score
    risk partner detection
    critical overdue alerts
    high priority alerts
    medium priority alerts
    low priority alerts
    finance escalation
    overdue escalation
    payment priority alerts
    account priority levels
    credit decision support
    financial workflow control
    internal finance tools
    partner debt summary
    late payment detection
    aging analytics
    partner overdue analytics
    payment timeline alerts
    priority-based alerts
    partner financial status
    invoice tracking
    bill tracking
    due account tracking
    aging summary alerts

    """,
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com",
    "depends": ["base", "account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/res_config_settings_views.xml",
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'license': 'OPL-1',
    "installable": True,
    "price": 25.00,
    "currency": 'USD',
    "application": True,
    "auto_install": False,
}