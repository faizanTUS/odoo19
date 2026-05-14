# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    "name": "Partner Mail Insights (Incoming/Outgoing)",
    "version": "18.0.1.0.0",
    "summary": (
        "Smart buttons on contacts for incoming and outgoing mail with counters "
        "and filtered list views."
    ),
    "description": """
Partner Mail Insights adds stat buttons on the contact form that open filtered
mail records (incoming vs outgoing) for the current partner, with live counters.
    """,
    "author": "TechUltra Solutions Private Limited",
    "website": "https://www.techultrasolutions.com",
    "category": "Contacts/mail",
    "license": "OPL-1",
    "depends": ["base", "contacts", "mail"],
    "data": [
        "views/res_partner_views.xml",
        "views/menu.xml",
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "price": 8.0,
    "currency": "EUR",
}
