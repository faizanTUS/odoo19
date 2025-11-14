# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    "name": "Odoo AI Chatbot | AIAgent | Odoo Smart Assistant | AskOdoo | Copilot AI | ChatGPT for Odoo",
    "version": "19.0.0.0",
    "category": "Tools ",
    "author": "TechUltra Solutions Private Limited",
    "company": "TechUltra Solutions Private Limited",
    "website": "https://www.techultrasolutions.com/",
    "summary": """
        This module uses AI logic to interpret natural language queries and return real-time, context-aware answers related to: Sales Orders (SO), Purchase Orders (PO), Invoices (Customer & Vendor), Whether you're a sales manager trying to track monthly deals, a procurement officer reviewing last week’s POs, or an accountant monitoring outstanding invoices, the Odoo AI Chatbot gives you answers in seconds, all within Odoo.
        AI Chatbot Odoo
        AI Chatbot
        Chatbot
        Chatbot Odoo
        Odoo Chatbot
        AI chatbot for Odoo
        Odoo chat
        AI
        Odoo AI
        Odoo bot
        ERP chatbot Odoo
        AIAgent
        Odoo Smart Assistant
        AskOdoo
        Copilot AI
        ChatGPT for Odoo
    """,
    "description": """
        Ask natural language questions and get answers based on Odoo database content.
    """,
    "depends": ["base"],
    "external_dependencies": {
        "python": [
            "langchain_community",
            "langchain_openai",
            "psycopg2",
            "langchain_google_genai",
            "faiss-cpu",
        ]
    },
    "data": [
        "security/ir.model.access.csv",
        "views/chatbot.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "odoo_ai_chatbot/static/src/scss/changes.scss",
            "odoo_ai_chatbot/static/src/js/chatbot.js",
            "odoo_ai_chatbot/static/src/xml/chatbot_view.xml",
        ],
    },
    "images": ["static/description/main_screen.gif"],
    "price": 359,
    "currency": "USD",
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}
