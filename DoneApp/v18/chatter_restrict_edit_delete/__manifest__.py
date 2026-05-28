# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Chatter Edit Restriction | Message Integrity Control | Advanced Mail Message Security',
    'version': '18.0.0.0',
    'summary': """This module enhances Odoo security by preventing users from editing or deleting existing log notes (`mail.message`) after creation. It helps maintain accurate communication history, improves accountability, and supports auditing and compliance requirements while still allowing users to create and view new log notes.
    TUS
    tus
    Techultra
    techultra
    techultra private limited solution
    Techultra Private Limited Solution
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
    This module adds an advanced security and control layer for Odoo log notes (`mail.message`) by restricting users from editing or deleting messages after they are created. Log notes are commonly used to track communications, activities, status updates, and internal discussions, and this module helps ensure that these records remain accurate, secure, and tamper-proof. It is especially useful for maintaining accountability, preserving communication history, and supporting auditing, reporting, and compliance requirements. Users can continue to create and view log notes normally, while modification and deletion permissions for existing records are restricted according to business policies.
    TUS
    tus
    Techultra
    techultra
    techultra private limited solution
    Techultra Private Limited Solution
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
            'chatter_restrict_edit_delete/static/src/core/common/message_inherit.js',
            'chatter_restrict_edit_delete/static/src/xml/chatter_views.xml',

        ]
    },
    'data': [
        'security/chatter_restrict_edit_delete_group.xml',
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    'installable': True,
    'auto_install': False,
    'price': 8.16,
    'currency': 'USD',
    'license': 'OPL-1',
}
