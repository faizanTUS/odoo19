{
    "name": "Cancel Sales Order (Cancel Picking (Delivery Order) and Invoice)",
    "version": "17.0.0.0.1",
    "category": "Sales",
    "summary": """
        Sale order, delivery, payment done but for some reason, the consumer canceled the Sales order. 
        We know that if we cancel SO, Odoo will simply cancel the sale order and nothing else. 
        Now you are worried how to manage it in odoo since odoo does not cancel invoice, delivery, and payments. 
        Don't worry, use tech ultra "sale order cancel" app to perform all tasks in single click.
    """,
    "description": 
    """ 
        Sales Order Cancel
        Delivery Cancel
        Invoice Cancel
        Invoice Reverese
        Cancel Sales Order
        Cancel Sales Flow
        Odoo Erp
        Odoo Sales Order Cancel
    """,
    "author": "TechUltra Solutions Private Limited",
    'company': 'TechUltra Solutions Private Limited',
    "website": "www.techultrasolutions.com",
    "depends": ["sale_management","sale_stock"],
    "images": [
        "static/description/main_screen.gif",
    ],
    "currency": "USD",
    "price": 9,
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "OPL-1",
}
