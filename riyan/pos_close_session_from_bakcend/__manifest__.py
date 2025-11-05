# See LICENSE file for full copyright and licensing details.
{
    "name": "POS Close Session From Backend",
    "version": "19.0.0.0",
    "category": "Point of Sale",
    "author": "TechUltra Solutions Private Limited",
    'company': 'TechUltra Solutions Private Limited',
    "website": "www.techultrasolutions.com",
    "summary": """ Odoo base allows you to close a session and post a journal entry from within the POS software, 
                   however it might be time consuming to open the POS app for each shop just to post a journal entry. \
                   To address this issue, we created an app that allows you to close and submit journal entries outside of the POS apps. Scroll below to know its functionality.
                    Close POS session externally
                    Post POS journal entry outside app
                    POS session management shortcut
                    Quick POS session close
                    External POS journal posting
                    Odoo POS backend control
                    Submit POS entries from backend
                    POS session automation Odoo
                    Close all POS sessions
                    Odoo POS session batch close
                    Journal entry posting without POS
                    Streamlined POS closing process
                    POS accounting integration Odoo
                    POS session backend actions
                    Multi-shop POS session control
                    Backend POS session wizard
                    Efficient POS journal posting
                    Non-POS interface journal posting
                    Close POS without opening frontend
                    Odoo POS admin tool

                   """,

    "description": """
                Odoo base allows you to close a session and post a journal entry from within the POS software, however it might be time consuming to open the POS app for each shop just to post a journal entry. To address this issue, we created an app that allows you to close and submit journal entries outside of the POS apps. Scroll below to know its functionality.
    
                Close POS session externally
                Post POS journal entry outside app
                POS session management shortcut
                Quick POS session close
                External POS journal posting
                Odoo POS backend control
                Submit POS entries from backend
                POS session automation Odoo
                Close all POS sessions
                Odoo POS session batch close
                Journal entry posting without POS
                Streamlined POS closing process
                POS accounting integration Odoo
                POS session backend actions
                Multi-shop POS session control
                Backend POS session wizard
                Efficient POS journal posting
                Non-POS interface journal posting
                Close POS without opening frontend
                Odoo POS admin tool

    """,
    "depends": ["point_of_sale"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/close_session_wizard.xml",
        "views/pos_session_view_inherit.xml",

    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    "currency": "USD",
    "price": 25,
    "application": False,
    "auto_install": False,
    "installable": True,
    "license": "OPL-1",
}
