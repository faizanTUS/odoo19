# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'POS Session Close & Journal Entry Posting | Backend POS Session Management',
    'version': '19.0.0.0',
    'author': 'TechUltra Solutions Private Limited',
    'category': 'Point of Sale',
    'website': 'https://www.techultrasolutions.com',
    "company": "TechUltra Solutions Private Limited",
    'summary': """
    Close POS sessions and generate journal entries from the backend without opening the POS interface, improving efficiency for multi-store and multi-terminal businesses.
    POS Session Close
    POS Session Closing
    POS Session Management
    POS Journal Entry Posting
    POS Session Close Odoo
    Odoo POS Session Close
    Odoo POS Journal Entry
    Point of Sale Session Management
    POS Accounting Entry
    POS Session Posting
    Odoo POS Session Closing
    Odoo POS Backend Management
    Odoo POS Accounting
    Odoo Point of Sale
    Odoo POS Session Control
    Odoo POS Operations
    Odoo POS Journal Posting
    Odoo POS Workflow
    Odoo POS Session Automation
    Odoo POS Backend Actions
    Close POS Session from Backend
    Odoo POS Session Close Without Opening POS
    Backend POS Session Management
    POS Session Closing and Journal Posting
    Odoo POS Journal Entry Posting
    Multi Store POS Session Management
    POS Session Close and Accounting Entry
    Point of Sale Session Closing Tool
    Odoo POS Session Automation
    Backend POS Closing Operations
    Multi Store POS Management
    POS Terminal Management
    Retail POS Management
    Backend POS Operations
    POS Administration
    POS Session Control
    POS Store Management
    Point of Sale Administration
    POS Workflow Automation
    POS Operational Efficiency
    """,
    'description': """
    POS Session Close & Journal Entry Posting extends Odoo's Point of Sale functionality by allowing users to close POS sessions and post related journal entries directly from the backend without accessing the POS interface. This streamlines session management for businesses operating multiple shops or POS terminals, reducing the time and effort required to process daily closing operations.
    POS Session Close
    POS Session Closing
    POS Session Management
    POS Journal Entry Posting
    POS Session Close Odoo
    Odoo POS Session Close
    Odoo POS Journal Entry
    Point of Sale Session Management
    POS Accounting Entry
    POS Session Posting
    Odoo POS Session Closing
    Odoo POS Backend Management
    Odoo POS Accounting
    Odoo Point of Sale
    Odoo POS Session Control
    Odoo POS Operations
    Odoo POS Journal Posting
    Odoo POS Workflow
    Odoo POS Session Automation
    Odoo POS Backend Actions
    Close POS Session from Backend
    Odoo POS Session Close Without Opening POS
    Backend POS Session Management
    POS Session Closing and Journal Posting
    Odoo POS Journal Entry Posting
    Multi Store POS Session Management
    POS Session Close and Accounting Entry
    Point of Sale Session Closing Tool
    Odoo POS Session Automation
    Backend POS Closing Operations
    Multi Store POS Management
    POS Terminal Management
    Retail POS Management
    Backend POS Operations
    POS Administration
    POS Session Control
    POS Store Management
    Point of Sale Administration
    POS Workflow Automation
    POS Operational Efficiency
    """,
    'depends': ['point_of_sale'],
    "data": [
        "security/ir.model.access.csv",
        "wizard/close_session_wizard.xml",
        "views/pos_session_view_inherit.xml",

    ],
    'images': [
        'static/description/main_screen.gif',
    ],
    'price': 24.95,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    "application": False,
}
