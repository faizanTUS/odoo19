# See LICENSE file for full copyright and licensing details.
{
    # App information
    "name": "Custom Currency Rate",
    "category": "Services/account",
    "summary": """
    Techultra Solutions Currency Rate App is a powerful and essential multi-functional tool designed for businesses dealing in multi-currency transactions. It simplifies currency rate management by automating exchange rate tracking and currency conversions across all key modules—Sales, Purchases, Invoicing, Credit/Debit Notes, and more—ensuring accuracy, saving time, and minimizing errors.
    Odoo currency rate app
    Multi-currency management in Odoo
    Odoo exchange rate automation
    Odoo currency converter
    Currency rate management Odoo
    Odoo multi-currency transactions
    Auto currency conversion Odoo
    Odoo currency exchange integration
    Convert foreign currency in Odoo
    Odoo invoice in multiple currencies
    Currency rate update for sales and purchase
    Multi-currency accounting in Odoo
    Real-time currency rate app
    Cross-border trade Odoo app
    Currency conversion for invoices, bills, and credit notes
    International trade automation in Odoo
    Odoo finance currency tool
    Odoo app for USD to INR conversion
    """,
    "description": """
        Managing transactions in multiple currencies can be complex and error-prone due to the daily fluctuations in exchange rates. For companies whose base currency is INR but engage in international trade using currencies like USD, the manual process of currency conversion can lead to time loss and inaccuracies that affect business operations.
        To address this, Techultra Solutions introduces the Currency Rate App, a smart and user-friendly
        Odoo currency rate app
    Multi-currency management in Odoo
    Odoo exchange rate automation
    Odoo currency converter
    Currency rate management Odoo
    Odoo multi-currency transactions
    Auto currency conversion Odoo
    Odoo currency exchange integration
    Convert foreign currency in Odoo
    Odoo invoice in multiple currencies
    Currency rate update for sales and purchase
    Multi-currency accounting in Odoo
    Real-time currency rate app
    Cross-border trade Odoo app
    Currency conversion for invoices, bills, and credit notes
    International trade automation in Odoo
    Odoo finance currency tool
    Odoo app for USD to INR conversion
        Rate
        Currency
        Currency Rate
        Odoo Currency Rate
        Custom Currency Rate
        Account Custom Currency Rate
        ERP
        Odoo ERP
        Accoun
        Accouning
        Invoice Custom Currency Rate
        Invoicing
        Invoice Custom Currency
        Exchange rate in Odoo
        Exchange rate
    """,
    "version": "19.0",
    "author": "TechUltra Solutions Private Limited",
    "license": "OPL-1",
    "company": "TechUltra Solutions Private Limited",
    "website": "https://www.techultrasolutions.com",
    # Dependencies
    "depends": ["sale", "base", "account", "sale_management", "purchase", "stock"],
    # Data
    "data": [
        "views/res_config.xml",
        "views/sale_order_view.xml",
        "views/stock_picking_view.xml",
        "views/purchase_order_view.xml",
        "views/account_move_view.xml",
        "views/account_payment.xml",
        "views/account_register_payment.xml",
    ],
    # Images
    "images": [
        "static/description/main_screen.gif"
    ],
    # Technical
    "currency": "USD",
    "price": 23,
    "installable": True,
    "auto_install": False,
    "application": False,
}
