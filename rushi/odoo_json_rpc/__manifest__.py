# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': "ODOO JSON RPC",
    'version': '19.0',
    'author': "TechUltra Solutions Private Limited",
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'category': 'Extra Tools',
    'license': 'OPL-1',
    'summary': """
    This module provides a powerful JSON-based API interface to access, manipulate, and extend Odoo records using both default and custom methods. It enables seamless integration with external systems and applications through structured JSON requests and responses.
    Odoo JSON API
    Odoo REST API
    Odoo API module
    Odoo external access API
    Odoo custom method API
    JSON interface for Odoo
    Odoo data access via JSON
    Odoo API integration
    Access Odoo records programmatically
    Odoo CRUD JSON API
    Execute custom methods in Odoo
    Odoo automation with JSON
    Odoo external system integration
    Odoo backend API
    JSON request Odoo
    Odoo API for mobile apps
    Odoo web service integration
    """,
    'description': """
    Unlock the full potential of Odoo with this JSON API module. It allows developers and third-party systems to interact with Odoo models using JSON-formatted requests. Whether you need to read, create, update, or execute custom methods on records, this module provides a flexible and secure way to do it via standard HTTP endpoints.
    Odoo JSON API
    Odoo REST API
    Odoo API module
    Odoo external access API
    Odoo custom method API
    JSON interface for Odoo
    Odoo data access via JSON
    Odoo API integration
    Access Odoo records programmatically
    Odoo CRUD JSON API
    Execute custom methods in Odoo
    Odoo automation with JSON
    Odoo external system integration
    Odoo backend API
    JSON request Odoo
    Odoo API for mobile apps
    Odoo web service integration
    """,
    'depends': ['base','mail','mail_bot'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/token.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 49.00,
    'currency': 'USD',
    'installable': True,
    'application': True,
}
