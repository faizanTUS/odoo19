# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Enhanced Sale Price History for Products',
    'version': '19.0.0.0',
    'author': 'TechUltra Solutions Private Limited',
    'category': 'Sales',
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com/',
    "summary": """Track product sale price history from quotations and sale orders with configurable order state filters.

    Odoo sale price history
    Odoo product price history
    Odoo sales price tracking
    Odoo product sale price history
    sale price history Odoo
    product price history Odoo
    sales price history module
    Odoo sales history by product
    product sales price tracker
    Odoo quotation price history
    Odoo sale order price history
    Odoo product pricing history
    Odoo historical sale prices
    Odoo product price tracker
    Odoo sale order line history
    Odoo sales price report
    Odoo product sales activity
    Odoo pricing trends
    Odoo sales module extension
    Odoo product sales history tab
    track product sale price history in Odoo
    view previous sale prices on product form in Odoo
    Odoo module to track sales price history
    show sale order price history on product page
    product wise sale price history in Odoo
    Odoo sales price history based on order state
    Odoo product price history from sale orders
    Odoo quotation and confirmed order price history
    configure sale price history records in Odoo
    display recent product sale prices in Odoo
    """,
    "description": """
    Enhanced Sale Price History helps businesses track and review previous sale prices directly from the product form in Odoo.

    The module adds a dedicated Sales Price History tab on the product template view. It displays recent product sale price records from sale order lines, including price, order reference, date, and order state.

    Users can configure which sale order states should be included in the history, such as Draft, Quotation Sent, and Confirmed Sale Orders. They can also define how many historical price records should be displayed for each product.

    This module is useful for sales teams, pricing managers, and business owners who want quick visibility into past product pricing without manually opening old quotations or sale orders.

    Key Features:
    - Track historical sale prices for each product automatically.
    - View sale price history directly on the product template form.
    - Display sale order reference, price, order date, and order state.
    - Configure the number of recent price history records to show.
    - Filter price history by Draft, Quotation Sent, and Confirmed Sale Orders.
    - Review product pricing trends and previous sales activity.
    - Reduce pricing mistakes while preparing quotations.
    - Improve sales visibility and pricing control.
    - Fully integrated with the standard Odoo Sales module.

    Business Benefits:
    - Helps sales users check previous product prices quickly.
    - Supports better quotation and price negotiation decisions.
    - Saves time by avoiding manual review of old sale orders.
    - Improves pricing transparency across the sales workflow.
    - Gives managers better control over product-wise sales pricing history.

    Recommended Keywords:
    Odoo sale price history, Odoo product price history, product sale price tracking, sales price history Odoo, sale order price history, quotation price history, product pricing history, Odoo sales module, historical sale prices, product price monitoring.
        """,
    "license": "OPL-1",
    'depends': ['sale_management', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_price_history_view.xml',
        'views/res_config_settings_view.xml',
        'data/data.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'installable': True,
    'application': False,
    'price': 12.00,
    'currency': 'EUR',
}
