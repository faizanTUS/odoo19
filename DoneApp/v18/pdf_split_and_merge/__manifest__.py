# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': 'Advanced PDF Split and Merge for Odoo | Extract Pages and Combine Files',
    'Version': '18.0.0.0',
    'category': 'Extra Tools',
    'author': 'Techultra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'summary': """
            Split, extract, merge, reorder, preview, and manage PDF files directly inside Odoo.
        """,
    'description': """
    Advanced PDF Split and Merge for Odoo | Extract Pages and Combine Files

    PDF Split and Merge is a powerful document management tool for Odoo that helps users split large PDF files, extract selected pages, merge multiple PDF documents, and reorder pages before generating the final PDF.

    This module is designed for businesses that regularly manage contracts, invoices, purchase orders, reports, legal documents, supplier documents, customer documents, and internal records.

    Key Features
    ------------
    * Split multi-page PDF files into individual PDF pages.
    * Extract selected pages from a PDF document.
    * Merge multiple PDF files into one organized PDF document.
    * Drag and drop PDF pages to reorder them before merging.
    * Preview PDF pages before finalizing the document.
    * Download split or merged PDF files quickly.
    * Manage PDF operations directly inside Odoo.
    * Simple and user-friendly backend interface.
    * Useful for document management, accounting, purchase, sales, and administration workflows.

    Business Benefits
    -----------------
    * Reduce manual PDF handling work.
    * Avoid using external PDF tools.
    * Improve document organization inside Odoo.
    * Save time while managing large PDF documents.
    * Keep PDF processing connected with Odoo records and attachments.

    Best Use Cases
    --------------
    * Split supplier invoices into separate documents.
    * Merge multiple customer documents into one PDF.
    * Extract required pages from contracts or reports.
    * Reorder pages before creating the final PDF.
    * Organize purchase orders, sales documents, invoices, and internal records.

    SEO Keywords
    ------------
    Odoo PDF split, Odoo PDF merge, split PDF in Odoo, merge PDF in Odoo, PDF management Odoo, Odoo document management, Odoo PDF tools, Odoo attachment PDF, Odoo document splitter, Odoo PDF organizer, PDF extract Odoo, PDF page reorder Odoo, PDF merge module Odoo, PDF split module Odoo.
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
        'python': ['fitz', 'Pillow'],
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
