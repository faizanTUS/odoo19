# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': 'PDF Split and Merge',
    'Version': '19.0.0.0',
    'category': 'Extra Tools',
    'author': 'Techultra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'summary': """
        Split and Merge PDF
        
        pdf
        split pdf
        merge pdf
        tus
        techultra
        techultra_private_limited_solution
        Odoo PDF split module
        Odoo PDF merge module
        PDF split and merge in Odoo
        Split PDF Odoo app
        Merge PDF Odoo module
        Odoo document split tool
        PDF tools for Odoo
        PDF management in Odoo
        Odoo split merge documents
        Odoo PDF editor module
        odoo
        odoo16
        odoo17
        odoo18
        odoo19
        How to split PDF files in Odoo
        Combine PDF files Odoo app
        Odoo DMS PDF tools
        PDF automation in Odoo
        Split multiple PDF pages Odoo
        Merge multiple PDFs in Odoo ERP
        Upload and organize PDFs in Odoo
        Odoo custom PDF handler
        Odoo PDF file organizer
        Document processing in Odoo
        Odoo PyPDF2 module        
        Odoo custom PDF widget        
        Odoo document workflow        
        Odoo record attachment PDF        
        Python PDF tools Odoo        
        PDF actions in Odoo backend        
        Odoo UI PDF integration
        odoo pdf split
        odoo pdf merge
        split pdf odoo
        merge pdf odoo
        odoo document tools
        odoo pdf organizer
        odoo document splitter
        odoo pdf handler
        odoo file management
        odoo document merge
        odoo dms
        odoo pdf manager
        odoo automation tools
        pypdf2 odoo
        odoo custom document module
    """,
    'description': """
        Efficiently split and merge PDF files inside Odoo. A user-friendly module for organizing, managing, and processing PDF documents seamlessly.
        
        pdf
        split pdf
        merge pdf
        tus
        techultra
        techultra_private_limited_solution
        Odoo PDF split module
        Odoo PDF merge module
        PDF split and merge in Odoo
        Split PDF Odoo app
        Merge PDF Odoo module
        Odoo document split tool
        PDF tools for Odoo
        PDF management in Odoo
        Odoo split merge documents
        Odoo PDF editor module
        odoo
        odoo16
        odoo17
        odoo18
        odoo19
        How to split PDF files in Odoo
        Combine PDF files Odoo app
        Odoo DMS PDF tools
        PDF automation in Odoo
        Split multiple PDF pages Odoo
        Merge multiple PDFs in Odoo ERP
        Upload and organize PDFs in Odoo
        Odoo custom PDF handler
        Odoo PDF file organizer
        Document processing in Odoo
        Odoo PyPDF2 module        
        Odoo custom PDF widget        
        Odoo document workflow        
        Odoo record attachment PDF        
        Python PDF tools Odoo        
        PDF actions in Odoo backend        
        Odoo UI PDF integration
        odoo pdf split
        odoo pdf merge
        split pdf odoo
        merge pdf odoo
        odoo document tools
        odoo pdf organizer
        odoo document splitter
        odoo pdf handler
        odoo file management
        odoo document merge
        odoo dms
        odoo pdf manager
        odoo automation tools
        pypdf2 odoo
        odoo custom document module

    """,
    'depends': ['mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/pdf_split_document_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pdf_split_and_merge/static/src/fields/**/*',
            'pdf_split_and_merge/static/src/xml/**/*',
            'pdf_split_and_merge/static/src/js/**/*',
            'pdf_split_and_merge/static/src/css/split_pdf.css',
        ],
    },
    'external_dependencies': {
        'python': ['fitz'], # PyMuPDF
    },
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 15.00,
    'currency': 'EUR',
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
