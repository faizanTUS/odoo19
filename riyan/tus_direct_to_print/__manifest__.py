# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Flexible PDF Report Actions in Odoo | Print, Download, or View Instantly',
    'summary': """Flexible PDF Report Handling in Odoo – No Third-Party Services Required A modal window is displayed with options for printing, downloading, and opening PDF documents. Customizable options simplify the handling of reports.
    Odoo print PDF without PrintNode
    Odoo direct PDF print
    Odoo report print from browser
    Odoo download PDF report
    Odoo open PDF in new tab
    Native PDF printing in Odoo
    Odoo report viewer
    Odoo custom report action
    Odoo report default behavior
    Odoo print without IoT box
    Odoo no third-party print solution
    Odoo report automation
    """,
    'version': '19.0.0.0',
    'description': """
    Handle PDF reports in Odoo effortlessly — print from browser, download to your device, or open in a new tab. No PrintNode or IoT box needed. Fully native and seamless.
       Odoo PDF report print, Odoo report download, Odoo open PDF report, Odoo print without PrintNode, native Odoo report handling, Odoo PDF preview, direct print Odoo, Odoo report customization, no IoT box Odoo
         Odoo print PDF without PrintNode
    Odoo direct PDF print
    Odoo report print from browser
    Odoo download PDF report
    Odoo open PDF in new tab
    Native PDF printing in Odoo
    Odoo report viewer
    Odoo custom report action
    Odoo report default behavior
    Odoo print without IoT box
    Odoo no third-party print solution
    Odoo report automation
    """,
    'author': 'TechUltra Solutions Private Limited',
    'license': 'OPL-1',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'category': 'Tools',

    'depends': ['web'],
    'data': [
        'views/ir_actions_report.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'tus_direct_to_print/static/src/xml/report_pdf_options.xml',
            'tus_direct_to_print/static/src/js/PdfPrintModal.js',
            'tus_direct_to_print/static/src/js/QwebactionManager.js',
        ]
    },
    "images": [
        "static/description/main_screen.gif",
    ],
    "currency": "USD",
    "price": 25.99,
    'installable': True,
    'auto_install': False,

}
