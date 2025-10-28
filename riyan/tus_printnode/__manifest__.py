# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    # App information
    "name": "Odoo Direct Print via Printnode",
    "category": "Tools",
    "summary": """
               Print Node odoo integration will provide you user friendly interface by which you can simplify  your printing experience, it will help you to print essential document from anywhere in the world using internet."
                This is one of the best app for cloud printing and direct printing.
                PrintNode Odoo integration
                Remote printing Odoo
                Odoo print solution
                Seamless document printing Odoo
                PrintNode for Odoo
                Cloud printing for Odoo
                Print from anywhere Odoo
                Odoo printing automation
                Odoo print setup
                Odoo printing without IoT box
                Simplify Odoo printing
                Odoo report printing solution
                Internet-based printing Odoo
               Odoo printing workflow
               Remote document printing Odoo
               """,
    "description": """ 
    PrintNode Odoo integration
    Remote printing Odoo
    Odoo direct print
    Odoo print solution
Seamless document printing Odoo
PrintNode for Odoo"
Cloud printing for Odoo
Print from anywhere Odoo
Odoo printing automation
Odoo print setup
Odoo printing without IoT box
Simplify Odoo printing
Odoo report printing solution
Internet-based printing Odoo
Odoo printing workflow
Remote document printing Odoo"
            Odoo direct print with network print
            odoo direct print Pro
            Odoo Direct Print (PrintNode)
            printnode base Odoo
            Odoo print directly to printer
            Odoo pos direct print
            Odoo 18 direct print
            How to print directly to printer
            Print Node
            Direct Print Via Print Node
            feature of direct print from Odoo by using PrintNode
            PrintNode
            Integrate PrintNode with Odoo
            Import Printers and Computer from PrintNode.
            Print any Odoo report directly to printer.
            download or print for each report
            Configure different printer
            Integrate multiple PrintNode accounts
            Print attachments by dynamic action
            instantly print invoices
            direct printer openerp
            prints the invoice without download
            Users can print any Odoo report or Shipping label
            Users can print any Odoo report or Shipping label to any network printer based printing any report or label from Odoo
             security measures for printing
            preview option before printing
            better cost management and optimization
            fetch all system & printers available in your system
            allowing cloud printing within any network.
            Only selected users will have permission to print invoices or reports
    """,
    "version": "19.0.0.0",
    "author": "TechUltra Solutions Private Limited",
    "license": "OPL-1",
    "company": "TechUltra Solutions Private Limited",
    "website": "https://www.techultrasolution.com",
    # Dependencies
    "depends": ["base"],
    "data": [
        "security/res_groups_view.xml",
        "security/ir.model.access.csv",
        "views/printnode_config.xml",
        "views/tus_printnode_sys.xml",
        "views/tus_printnode_printer.xml",
        "views/ir_action_report_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "tus_printnode/static/src/**/*.xml",
            "tus_printnode/static/src/js/web_action_manager_updated.js",
            "tus_printnode/static/src/js/Pdf_Options_Modal.js",
            # "tus_printnode/static/src/js/action_manager.js",
        ],
    },
    "images": [
        "static/description/main_screen.gif",
    ],
    # Technical
    "price": 99.00,
    "currency": "USD",
    "installable": True,
    "auto_install": False,
    "application": False,
}
