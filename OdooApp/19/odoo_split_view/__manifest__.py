# Part of Techultra. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Odoo Split View',
    'version': '19.0.0.0',
    'category': 'Extra Tools',
    'author': 'Techultra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'summary': """
    Modern split view: work with list and record side-by-side for faster workflow
    
    tus
    techultra
    techultra_private_limited_solution
    odoo split view
    split view
    split
    odoo side by side view
    odoo dual panel view
    odoo split list and form
    odoo split form editor
    odoo list form side panel
    odoo split view productivit
    odoo split record form
    odoo split layout toggle
    odoo vertical horizontal split
    odoo split view module
    odoo iframe form embedding
    odoo improve record navigation
    odoo realtime record sync
    odoo split view customization
    odoo split form and list editing
    odoo split view module
    odoo side-by-side form view
    odoo split panel editor
    odoo list and form view enhancement
    odoo dual panel editing
    odoo split view productivity boost
    odoo vertical horizontal view switch
    odoo real-time list form sync
    odoo split form navigation
    odoo iframe embedded form view
    odoo split layout customization
    odoo enhanced record editor
    odoo split record management
    odoo fast record editing
    odoo efficient record handling
    odoo iframe security bypass plugin
    odoo advanced form and list view
    odoo side panel record editor
    odoo form list splitter
    odoo user-friendly split view
    odoo multi-view interface
    odoo productivity extension
    odoo enterprise split view
    odoo record and list dual panel
    odoo split view dashboard integration
    odoo split view record editor
    odoo efficient side-by-side editor
    odoo split view interface productivity
    odoo record management split view
    odoo split panel list form integration
    odoo advanced split form navigation
    odoo split record form editor plugin
    odoo customizable split view layout
    odoo fast dual view record editing
    odoo split view with live sync
    odoo iframe split view solution
    odoo split view user preference toggle
    odoo split view interface for enterprise
    odoo list form workflow optimization
    odoo split panel multi-record editor
    odoo vertical horizontal view switcher
    odoo split view for complex operations
    odoo split view for multi-tasking
    odoo split view productivity extension
    odoo advanced record side panel editor
    
    """,
    'description': """
Split View for Odoo
======================

Effortlessly view and edit records side-by-side with the Odoo Split View extension.
Ideal for sales, inventory, and operations teams who want immediate access to both list and detailed record panels.

Key Highlights:
---------------
- Instantly open records in a split panel (vertical or horizontal) next to the main list view.
- Real-time synchronization: editing a record updates the list panel automatically.
- One-click switching between vertical and horizontal layout.
- Responsive design: works on all screen sizes.
- Prevents overlapping split panels for a clean, professional UX.
- Lightweight, fully client-side (no backend code required).
- Easy integration and removal—no data migration needed.

**Important Requirement:**
--------------------------
If you use split form panels via iframe, you must install a browser plugin such as "Ignore X-Frame headers" (available for Chrome/Edge/Firefox).
This allows embedded Odoo forms to load in iframes; otherwise, browser security may block content due to X-Frame-Options headers.

Designed for Odoo Community & Enterprise.


tus
techultra
techultra_private_limited_solution
odoo split view
split view
split
odoo side by side view
odoo dual panel view
odoo split list and form
odoo split form editor
odoo list form side panel
odoo split view productivit
odoo split record form
odoo split layout toggle
odoo vertical horizontal split
odoo split view module
odoo iframe form embedding
odoo improve record navigation
odoo realtime record sync
odoo split view customization
odoo split form and list editing
odoo split view module
odoo side-by-side form view
odoo split panel editor
odoo list and form view enhancement
odoo dual panel editing
odoo split view productivity boost
odoo vertical horizontal view switch
odoo real-time list form sync
odoo split form navigation
odoo iframe embedded form view
odoo split layout customization
odoo enhanced record editor
odoo split record management
odoo fast record editing
odoo efficient record handling
odoo iframe security bypass plugin
odoo advanced form and list view
odoo side panel record editor
odoo form list splitter
odoo user-friendly split view
odoo multi-view interface
odoo productivity extension
odoo enterprise split view
odoo record and list dual panel
odoo split view dashboard integration
odoo split view record editor
odoo efficient side-by-side editor
odoo split view interface productivity
odoo record management split view
odoo split panel list form integration
odoo advanced split form navigation
odoo split record form editor plugin
odoo customizable split view layout
odoo fast dual view record editing
odoo split view with live sync
odoo iframe split view solution
odoo split view user preference toggle
odoo split view interface for enterprise
odoo list form workflow optimization
odoo split panel multi-record editor
odoo vertical horizontal view switcher
odoo split view for complex operations
odoo split view for multi-tasking
odoo split view productivity extension
odoo advanced record side panel editor


""",
    'depends': ['base', 'web'],
    'assets': {
        'web.assets_backend': [
            'odoo_split_view/static/src/js/*.js',
            'odoo_split_view/static/src/xml/*.xml',
            'odoo_split_view/static/src/scss/*.scss',
        ],
    },
    "images": [
        "static/description/main_screen.gif",
    ],
    'currency': 'USD',
    'price': 35.00,
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}
