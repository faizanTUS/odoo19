# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    "name": "TUS Product Barcode Generator",
    "version": "19.0.0.0",
    "category": "Inventory",
    'author': 'Techultra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    "summary": """Auto generate barcode for products manually or in bulk
        tus
        techultra
        techultra_private_limited_solution
        Barcode generator
        Generate product barcodes
        Barcode type selection
        Automatic barcode generation
        QR code with name
        Multi barcode generation
        Barcode configuration settings
        Product barcode system
        Barcode length validation
        Barcode preview feature
        Odoo barcode generator
        Barcode app for Odoo
        Odoo product barcode
        Generate barcode in Odoo
        Odoo QR code generator
        Odoo multi barcode tool
        Barcode configuration Odoo
        Odoo barcode type selection
        Auto-generate barcode Odoo
        Odoo barcode override option
        odoo
        odoo16
        odoo17
        odoo18
        odoo19
        How to generate barcodes for products in Odoo
        Automatically create barcodes in Odoo product form
        Odoo module for bulk barcode generation
        Multi-product barcode generation in Odoo
        Barcode preview and configuration in Odoo
        QR code with product name in Odoo
        Odoo barcode generator with prefix and length setup
        Validate barcode length by type in Odoo
        Custom barcode types in Odoo inventory
        Odoo barcode generation popup settings
        Best barcode generator app for Odoo
    """,
    'description': """Barcode Generator for Products - Odoo
        This app allows you to automatically generate barcodes or QR codes for products in Odoo. You can configure barcode types, length, prefix, and override options directly from the product form or in bulk.
        tus
        techultra
        techultra_private_limited_solution
        Barcode generator
        Generate product barcodes
        Barcode type selection
        Automatic barcode generation
        QR code with name
        Multi barcode generation
        Barcode configuration settings
        Product barcode system
        Barcode length validation
        Barcode preview feature
        Odoo barcode generator
        Barcode app for Odoo
        Odoo product barcode
        Generate barcode in Odoo
        Odoo QR code generator
        Odoo multi barcode tool
        Barcode configuration Odoo
        Odoo barcode type selection
        Auto-generate barcode Odoo
        Odoo barcode override option
        odoo
        odoo16
        odoo17
        odoo18
        odoo19
        How to generate barcodes for products in Odoo
        Automatically create barcodes in Odoo product form
        Odoo module for bulk barcode generation
        Multi-product barcode generation in Odoo
        Barcode preview and configuration in Odoo
        QR code with product name in Odoo
        Odoo barcode generator with prefix and length setup
        Validate barcode length by type in Odoo
        Custom barcode types in Odoo inventory
        Odoo barcode generation popup settings
        Best barcode generator app for Odoo
    """,
    "depends": ["product", "stock", "base"],
    "data": [
        "security/ir.model.access.csv",
        "security/product_barcode_security.xml",
        "views/product_views.xml",
        "views/res_config_settings_views.xml",
        "views/generate_barcode_wizard_views.xml"
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 14.14,
    'currency': 'USD',
    "license": "OPL-1",
    "installable": True,
    'auto_install': False,
}
