# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Restrict chatter Edit and Delete',
    'version': '17.0',
    'summary': """Restricts editing and deleting log notes in Odoo 17. 
    
    TUS
    tus
    Techultra
    techultra
    techultra private limited solution
    Techultra Private Limited Solution
    odoo 16
    odoo 17
    odoo 18
    Odoo restrict chatter
    chatter restrict edit delete
    chatter
    edit restriction
    delete restriction
    log note
    mail.message
    message contro
    security
    audit
    compliance
    permissions
    user access
    tamper proof
    internal communication,
    Odoo module
    chatter security
    access rights
    Disable chatter edit Odoo
    Prevent chatter delete Odoo
    Lock mail.message Odoo
    Odoo chatter control
    Secure log notes Odoo
    Chatter message restrictions Odoo
    Odoo audit trail chatter
    Chatter edit delete restriction
    Odoo communication history lock
    Odoo log note protection
    Odoo restrict message modification
    Odoo chatter security module
    No delete chatter Odoo
    Immutable chatter messages Odoo
    Restrict internal notes Odoo
    Odoo message tamper-proof
    Odoo compliance chatter
    Chatter edit rights Odoo
    Odoo message edit control
    Odoo chatter edit restriction
    Odoo restrict message editing
    Block chatter deletion Odoo
    Odoo restrict note deletion
    Disable log note editing Odoo
    Lock chatter messages Odoo
    Make chatter read-only Odoo
    Odoo disable chatter changes
    Prevent message editing Odoo
    Secure chatter entries Odoo
    Odoo chatter audit compliance
    Odoo message integrity
    Tamper-proof chatter Odoo
    Chatter change history Odoo
    Preserve chatter logs Odoo
    Odoo log audit trail
    Odoo chatter history protection
    Secure internal communication Odoo
    Odoo chatter security enhancement
    Odoo mail.message control
    Odoo technical log note restriction
    Prevent mail.message write Odoo
    Control message update Odoo
    Odoo chatter control module
    Message thread security Odoo
    
    """,
    'description': """
        This module restricts the ability to edit and delete log notes (mail.message) in Odoo 17.
        It includes custom security rules and view modifications to enforce these restrictions.
        
    TUS
    tus
    Techultra
    techultra
    techultra private limited solution
    Techultra Private Limited Solution
    odoo 16
    odoo 17
    odoo 18
    Odoo restrict chatter
    chatter restrict edit delete
    chatter
    edit restriction
    delete restriction
    log note
    mail.message
    message contro
    security
    audit
    compliance
    permissions
    user access
    tamper proof
    internal communication,
    Odoo module
    chatter security
    access rights
    Disable chatter edit Odoo
    Prevent chatter delete Odoo
    Lock mail.message Odoo
    Odoo chatter control
    Secure log notes Odoo
    Chatter message restrictions Odoo
    Odoo audit trail chatter
    Chatter edit delete restriction
    Odoo communication history lock
    Odoo log note protection
    Odoo restrict message modification
    Odoo chatter security module
    No delete chatter Odoo
    Immutable chatter messages Odoo
    Restrict internal notes Odoo
    Odoo message tamper-proof
    Odoo compliance chatter
    Chatter edit rights Odoo
    Odoo message edit control
    Odoo chatter edit restriction
    Odoo restrict message editing
    Block chatter deletion Odoo
    Odoo restrict note deletion
    Disable log note editing Odoo
    Lock chatter messages Odoo
    Make chatter read-only Odoo
    Odoo disable chatter changes
    Prevent message editing Odoo
    Secure chatter entries Odoo
    Odoo chatter audit compliance
    Odoo message integrity
    Tamper-proof chatter Odoo
    Chatter change history Odoo
    Preserve chatter logs Odoo
    Odoo log audit trail
    Odoo chatter history protection
    Secure internal communication Odoo
    Odoo chatter security enhancement
    Odoo mail.message control
    Odoo technical log note restriction
    Prevent mail.message write Odoo
    Control message update Odoo
    Odoo chatter control module
    Message thread security Odoo
    """,
    'author': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultrasolutions.com',
    'category': 'Tools',
    'depends': ['mail'],  # Depends on the 'mail' module for log notes (mail.message)
    'assets': {
        'web.assets_backend': [
            'chatter_restrict_edit_delete/static/src/xml/chatter_views.xml',
            'chatter_restrict_edit_delete/static/src/core/common/message_inherit.js',
        ]
    },
    'data': [
        'security/chatter_restrict_edit_delete_group.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'installable': True,
    'price': 7,
    'currency': 'EUR',
    'auto_install': False,
    'license': 'OPL-1',
}
