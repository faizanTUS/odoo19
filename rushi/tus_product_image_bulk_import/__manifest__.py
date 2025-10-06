{
    'name': 'Product Image Import',
    'category': 'Product',
    'version': '19.0.0.0',
    'author': "TechUltra Solutions Private Limited",
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'summary': """Bulk import product images using a zip file with images named after product identifiers.
                Odoo Bulk Product Image Import
                Import Product Images via ZIP Odoo
                Odoo ZIP Image Upload for Products
                Odoo Product Image Import by Identifier
                Mass Image Import Odoo Products
                Odoo Product Image Bulk Upload
                Auto Match Product Images Odoo
                Odoo Import Product Images from ZIP
                Odoo Product Image Mapping by Code
                Bulk Product Photo Upload Odoo
                Upload multiple product images in Odoo using ZIP
                Bulk import product images by product code
                Odoo image import by product internal reference
                ZIP file import for product pictures in Odoo
                Odoo product image automation from zip file
                Assign product images in bulk using filenames
                Mass upload product photos Odoo backend
                Odoo auto-detect product images from zip
                Import product media using product SKU in Odoo
                Streamlined product image upload for Odoo
                Product catalog image management
                ERP media import automation
                Odoo product data enrichment
                E-commerce product image sync Odoo
                Product image batch processing
                Inventory image update tool Odoo
                Product photo upload module
                Product media mapping
                Visual product identification Odoo
                Odoo product file import utility
    """,
    'description': """ This module allows users to import product images in bulk via a zip file. The images can be named after the product's Internal Reference, Barcode, or Display name. The module provides feedback on successful imports and notifies if any products are not found.
                        Odoo Bulk Product Image Import
                        Import Product Images via ZIP Odoo
                        Odoo ZIP Image Upload for Products
                        Odoo Product Image Import by Identifier
                        Mass Image Import Odoo Products
                        Odoo Product Image Bulk Upload
                        Auto Match Product Images Odoo
                        Odoo Import Product Images from ZIP
                        Odoo Product Image Mapping by Code
                        Bulk Product Photo Upload Odoo
                        Upload multiple product images in Odoo using ZIP
                        Bulk import product images by product code
                        Odoo image import by product internal reference
                        ZIP file import for product pictures in Odoo
                        Odoo product image automation from zip file
                        Assign product images in bulk using filenames
                        Mass upload product photos Odoo backend
                        Odoo auto-detect product images from zip
                        Import product media using product SKU in Odoo
                        Streamlined product image upload for Odoo
                        Product catalog image management
                        ERP media import automation
                        Odoo product data enrichment
                        E-commerce product image sync Odoo
                        Product image batch processing
                        Inventory image update tool Odoo
                        Product photo upload module
                        Product media mapping
                        Visual product identification Odoo
                        Odoo product file import utility
    """,
    'depends': ['base', 'product', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/import_image_wizard.xml',
        'wizard/import_image_results.xml',
        'views/product_image_import_menu.xml',

    ],
"images": [
        "static/description/main_screen.gif",
    ],
    'category': 'tool',
    'license': 'OPL-1',
    'price': 16.99,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': True,
}
