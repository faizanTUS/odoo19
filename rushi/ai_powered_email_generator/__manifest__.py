# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'AI Powered Email Generator',
    'description': """Enhance your email communication with the AI-Powered Email Generator.
                    This intelligent module utilizes AI to dynamically create personalized and professional emails based on selected fields. 
                    Whether it's order confirmations, follow-ups, or other business correspondence, 
                    this solution ensures accurate, efficient, and automated email generation, reducing manual effort while maintaining precision.""",
    'summary': """Automate and streamline email communication in Odoo with AI-driven efficiency.
                The AI-Powered Email Generator dynamically crafts professional emails based on selected fields,
                 optimizing workflows, improving accuracy, and enhancing customer engagement.
                AI Email Automation
                Email Personalization in Odoo
                Smart Email Generator
                Automated Customer Emails
                Dynamic Email Solutions
                AI-Powered Email Customization
                Business Email Automation
                Efficient Email Management
                Professional Email Generator
                Automated Email Templates
                Odoo Communication Tools
                Intelligent Email Automation
                AI Email Personalization Tools
                Odoo Workflow Optimization
                AI Email Assistant
                Email Correspondence Automation
                AI-Driven Email Management
                Precision Email Crafting
                AI in Business Communication
                Customer Engagement Automation
                Odoo Email Generation
                Email Template Automation
                AI-Powered Email Engine
                Odoo Module for Emails
                AI Email Correspondence
                Smart Email Workflow
                Odoo AI Email System
                Professional Correspondence in Odoo
                AI Email Enhancements
                Email Streamlining with AI
                Odoo Business Email Module
                AI Email Solutions for Odoo
                Automated Order Emails
                Smart Follow-Up Emails
                AI for Customer Communication
                Advanced Email Automation
                AI-Driven Email Features
                Workflow-Optimized Emails
                Odoo AI Integration
                Personalized Email Workflows""",
    'sequence': 10,
    'version': '18.0',
    'category': 'Tools',
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolution.com',
    'price': 49,
    'currency': 'EUR',
    'depends': ['mail'],
    'data': [
        'wizard/mail_compose_message_views.xml',
        'views/res_config_settings_views.xml'
    ],
   'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'assets': {
        'web.assets_backend': [
            'ai_powered_email_generator/static/src/css/email_highlight.css',
        ],
    },
    "images": ["static/description/main_banner.gif"],
}