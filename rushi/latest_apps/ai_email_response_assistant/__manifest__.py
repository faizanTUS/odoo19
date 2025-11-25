# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'AI Email Response Assistant',
    'description': """Enhance your email communication with the AI Email Response Assistant. 
                    This intelligent module analyzes recent email conversations to generate context-aware, professional responses instantly.
                    Powered by AI, it delivers accurate, relevant, and efficient replies, saving time while improving communication quality and consistency.""",
    'summary': """Automate email responses with AI-driven contextual analysis. 
                The AI Email Response Assistant intelligently crafts personalized replies by analyzing recent email threads,
                 minimizing manual effort, and streamlining communication workflows.  
                AI Email Response Assistant
                Context-Aware Email Replies
                Automated Email Responses
                AI Email Analysis Module
                Smart Email Replies in Odoo
                Email Response Automation
                AI-Powered Email Assistant
                Contextual Email Responses
                Intelligent Email Reply Generator
                AI for Email Communication
                Professional Email Replies
                AI Email Workflow Optimization
                Odoo Email Response Automation
                Personalized Email Responses
                Efficient Email Management
                AI-Driven Communication Tools
                Contextual Email Reply Automation
                Smart Reply Generator for Odoo
                AI Email Conversation Analysis
                AI-Powered Email Automation
                Accurate Email Replies
                Business Email Response Automation
                Email Workflow Enhancement
                Intelligent Communication Tools
                AI Response Generator
                Email Consistency Automation
                Contextual Communication in Odoo
                AI-Enhanced Email Tools
                Odoo Email Reply Module
                AI Email Context Analysis
                Automated Business Correspondence
                AI Tools for Email Management
                Workflow-Driven Email Replies
                Odoo Communication Automation
                AI Solutions for Email
                Customer Communication Automation
                Streamlined Email Responses
                Advanced Email Management with AI
                Email Assistant for Odoo
                AI-Generated Professional Replies
                """,
    'version': '19.0.0.0',
    'category': 'Tools',
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com',
    'price': 59,
    'currency': 'EUR',
    'depends': ['mail','base_setup'],
    'data': [
        'wizard/mail_compose_message_views.xml',
        'views/res_config_settings_views.xml'
    ],
    'external_dependencies': {
        'python': ['langchain','langchain_google_genai','pydantic',],
    },
    "images": ["static/description/main_banner.gif"],
   'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
}





