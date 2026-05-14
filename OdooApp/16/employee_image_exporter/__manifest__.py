# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    "name": "Advanced Employee Image Exporter",
    "version": "16.0.0.0",
    "category": "Human Resources",
    "author": "TechUltra Solutions Private Limited",
    'company': 'TechUltra Solutions Private Limited',
    "website": "https://www.techultrasolutions.com/",
    "summary": """
    The Advanced Employee Image Exporter module adds a powerful image-exporting tool to Odoo’s Employee Management. It allows users to export images for all, selected, or domain-filtered employees with options to include archived records. The module offers flexible file naming patterns, multiple output formats, and image resizing capabilities. All exports are delivered in a structured ZIP file. Additionally, access-controlled export logs ensure only authorized users can view the export history and see who executed each operation.
    Odoo employee image export
    Odoo image exporter module
    Export employee photos Odoo
    Odoo HR image download
    Bulk employee image export
    Odoo employee photo ZIP download
    Employee image management Odoo
    Odoo custom image exporter
    Odoo employee photo resizing
    Advanced image export Odoo
    Odoo HR tools module
    Employee images ZIP export
    Odoo employee archive export
    Odoo employee domain filter export
    File naming patterns Odoo
    Odoo employee photo format conversion
    Export employee JPEG PNG
    Odoo image resizing module
    HR image export solution Odoo
    Download employee images Odoo
    Employee photo automation Odoo
    Odoo employee export logs
    Access controlled image export Odoo
    Odoo HR documentation tools
    Employee photo backup Odoo
    Odoo bulk image downloader
    Export employee image variants
    Odoo custom export patterns
    Odoo HR compliance image export
    Odoo employee image management
    Odoo18
    Odoo17
    Odoo16
    TUS
    tus
    techultra solutions
    techultra
    techultra solutions private limited
    """,
    "description": """
    The Advanced Employee Image Exporter module enhances Odoo’s Employee Management by providing a flexible tool to export employee images with advanced customization. Users can export images for all employees, selected employees, or domain-filtered records, with an option to include archived employees.It supports dynamic file naming patterns (name, identification number, record ID, or custom formats), multiple output formats (Original, JPEG, PNG), and optional image resizing. All images are packaged into a clean ZIP file for easy use in HR documentation, ID cards, audits, or backups.The module also includes access-controlled export logs, allowing only assigned users to view export history and track who performed each image export operation.
    Odoo employee image export
    Odoo image exporter module
    Export employee photos Odoo
    Odoo HR image download
    Bulk employee image export
    Odoo employee photo ZIP download
    Employee image management Odoo
    Odoo custom image exporter
    Odoo employee photo resizing
    Advanced image export Odoo
    Odoo HR tools module
    Employee images ZIP export
    Odoo employee archive export
    Odoo employee domain filter export
    File naming patterns Odoo
    Odoo employee photo format conversion
    Export employee JPEG PNG
    Odoo image resizing module
    HR image export solution Odoo
    Download employee images Odoo
    Employee photo automation Odoo
    Odoo employee export logs
    Access controlled image export Odoo
    Odoo HR documentation tools
    Employee photo backup Odoo
    Odoo bulk image downloader
    Export employee image variants
    Odoo custom export patterns
    Odoo HR compliance image export
    Odoo employee image management
    Odoo18
    Odoo17
    Odoo16
    TUS
    tus
    techultra solutions
    techultra
    techultra solutions private limited
    """,
    "depends": ["base", "hr"],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "wizards/employee_image_export_wizard_view.xml",
        "views/employee_image_export_log_views.xml",
    ],
    "images": ["static/description/main_screen.gif"],
    "price": 12.00,
    "currency": "USD",
    "installable": True,
    'auto_install': False,
    "application": True,
    "license": "OPL-1",
}
