# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    # App information
    'name': 'Global Record Sorting Manager | Default List View Sorting | Odoo Data Ordering',
    'category': 'Sorting Record',
    'summary': """Sorting Record.
                Odoo Record Sorting
                Sort Records in Odoo
                Odoo Data Sorting Feature
                Odoo Ascending Descending Sort
                Odoo Sort by Field
                Record Order Management Odoo
                Odoo Sort List View
                Odoo Sorting Tool
                Odoo Default Sort Order
                Odoo Custom Record Sorting
                Sort Odoo records by date or name
                Ascending and descending sort in Odoo list view
                How to sort records in Odoo backend
                Odoo module for sorting data
                Default sort field in Odoo views
                Organize Odoo data with sorting
                Custom record ordering in Odoo views
                Odoo tree view sorting by field
                Manage record display order in Odoo
                Odoo dynamic record sorting
                Odoo list view enhancements
                ERP data presentation control
                Record display customization Odoo
                Sorting functionality in Odoo
                View-level data management Odoo
                Backend UI customization Odoo
                Field-based record ordering
                Sorting configuration in Odoo views
                Data organization Odoo ERP
                Sort logic implementation in Odoo

    """,
    'description': """Odoo Sorting Record
    Sorting records are a way to organize and display data in a specific order, typically in ascending (from lowest to highest) or descending (from highest to lowest) order.
    Ascending Order
    Descending Order
    Odoo Record Sorting
    Sort Records in Odoo
    Odoo Data Sorting Feature
    Odoo Ascending Descending Sort
    Odoo Sort by Field
    Record Order Management Odoo
    Odoo Sort List View
    Odoo Sorting Tool
    Odoo Default Sort Order
    Odoo Custom Record Sorting
    Sort Odoo records by date or name
    Ascending and descending sort in Odoo list view
    How to sort records in Odoo backend
    Odoo module for sorting data
    Default sort field in Odoo views
    Organize Odoo data with sorting
    Custom record ordering in Odoo views
    Odoo tree view sorting by field
    Manage record display order in Odoo
    Odoo dynamic record sorting
    Odoo list view enhancements
    ERP data presentation control
    Record display customization Odoo
    Sorting functionality in Odoo
    View-level data management Odoo
    Backend UI customization Odoo
    Field-based record ordering
    Sorting configuration in Odoo views
    Data organization Odoo ERP
    Sort logic implementation in Odoo

    """,
    'version': '18.0.0.0',
    'author': 'TechUltra Solutions Private Limited',
    'license': 'OPL-1',
    'company': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolution.com',

    # Dependencies
    'depends': ['web','base'],

    "data": [

        'security/ir.model.access.csv',
        'security/res_groups_view.xml',
        'views/sorting_record.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    # Technical
    'price': 10.00,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': True,
}
