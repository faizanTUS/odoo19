# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    "name": "Section Collapse Advanced",
    "version": "19.0.1.0.0",
    "category": "Productivity",
    "author": "TechUltra Solutions Private Limited",
    "company": "TechUltra Solutions Private Limited",
    "maintainer": "TechUltra Solutions Private Limited",
    "website": "https://www.techultrasolutions.com/",
    "summary": "Collapse and expand grouped section lines on quotations, sale orders, "
               "invoices and purchase orders for cleaner, faster document review.",
    "description": """
Section Collapse Advanced
=========================

Adds collapsible / expandable sections to Odoo document line lists (sale orders,
quotations, invoices, purchase orders, and any model that uses `o_is_line_section`
rows). With a single click, users can hide or show all lines belonging to a section
to reduce clutter and navigate large documents faster.

Key capabilities
----------------

* One-click collapse / expand of any section row
* Live "N items - Expand / Collapse" indicator on every section
* Works on standard Odoo list editors (sale, purchase, invoice, etc.)
* Lightweight client-side only - no server load, no schema changes
* Compatible with Odoo Community and Enterprise editions

Highlights
----------

* Improves readability of long quotations and orders
* Speeds up navigation when reviewing grouped line items
* No configuration required - works out of the box after install
""",
    "depends": ["web", "sale"],
    "assets": {
        "web.assets_backend": [
            "section_collapse_advanced/static/src/js/section_collapse.js",
            "section_collapse_advanced/static/src/scss/section_collapse.scss",
        ],
    },
    "images": ["static/description/main_screen.gif"],
    "price": 29.99,
    "currency": "USD",
    "installable": True,
    "auto_install": False,
    "application": False,
    "license": "OPL-1",
}
