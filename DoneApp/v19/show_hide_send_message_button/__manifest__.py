# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
{
    "name": "Show Hide Send Message Button | Chatter Access Control | User-Based Messaging Permissions",
    "version": "19.0.0.0",
    "author": "TechUltra Solutions Private Limited",
    "category": "Discuss",
    "company": "TechUltra Solutions Private Limited",
    "website": "https://www.techultrasolutions.com/",
    "summary": """
                In Odoo, administrators can control the visibility of the "Send Message" button in the chatter for specific users. This feature allows administrators to easily manage which users can send messages directly from the record's discussion layout. The configuration is accessible through the user settings panel, ensuring a streamlined process to enable or disable message-sending functionality for individual users.
                Odoo message button control
                Odoo user access management
                Odoo chatter customization
                Odoo send message button permissions
                Restrict message sending in Odoo
                Odoo user settings panel
                Manage Odoo message visibility
                Odoo user permissions chatter
                Odoo hide send message button
                Odoo access control for messaging
                Customizable message button Odoo 
                Odoo Hide Send Message Button
                Odoo Chatter Button Control
                Odoo Disable Send Message for Users
                Odoo Chatter Permissions
                Odoo Chatter Restriction by User
                Hide Chatter Button Odoo
                Restrict Send Message Odoo
                Odoo Disable Messaging Per Model
                Odoo User-Specific Chatter Control
                Odoo Chatter Access Management
                Odoo Chatter Message Restriction
                Odoo Hide Chatter Options
                Odoo Disable Messaging in Chatter
                Odoo Chatter Customization
                Odoo Chatter Access Control
                Odoo Chatter Send Message Visibility
                Chatter Button Visibility Odoo
                Odoo Hide Message Button by User
                Odoo Custom Chatter Permissions
                Odoo Chatter User Restriction Module
                Odoo Per User Chatter Permissions
                Hide Chatter Button Odoo for Specific Users
                Disable Chatter Messaging for Internal Users in Odoo
                Restrict Chatter Send Option Odoo User Settings
                Odoo User-Level Chatter Control
                Role-Based Chatter Message Control in Odoo
                Hide Send Message Button Based on User Access Rights
                Per Model Send Message Control Odoo
                Custom Model Chatter Button Hide Odoo
    """,
    "description": """
                This functionality empowers administrators to set access permissions for the "Send Message" button on a per-user basis in Odoo. Through the user settings panel, admins can enable or disable this feature for each user, ensuring that only authorized users can interact with the chatter and send messages. When disabled, the button is hidden from the discussion layout, preventing unauthorized users from sending messages. This customization enhances the user access control and streamlines the management of communication features within Odoo.
                Odoo message button control
                Odoo user access management
                Odoo chatter customization
                Odoo send message button permissions
                Restrict message sending in Odoo
                Odoo user settings panel
                Manage Odoo message visibility
                Odoo user permissions chatter
                Odoo hide send message button
                Odoo access control for messaging
                Customizable message button Odoo 
                Odoo Chatter Button Control
                Odoo Disable Send Message for Users
                Odoo Chatter Permissions
                Odoo Chatter Restriction by User
                Hide Chatter Button Odoo
                Restrict Send Message Odoo
                Odoo Disable Messaging Per Model
                Odoo User-Specific Chatter Control
                Odoo Chatter Access Management
                Odoo Chatter Message Restriction
                Odoo Hide Chatter Options
                Odoo Disable Messaging in Chatter
                Odoo Chatter Customization
                Odoo Chatter Access Control
                Odoo Chatter Send Message Visibility
                Chatter Button Visibility Odoo
                Odoo Hide Message Button by User
                Odoo Custom Chatter Permissions
                Odoo Chatter User Restriction ModuleOdoo Per User Chatter Permissions
                Hide Chatter Button Odoo for Specific Users
                Disable Chatter Messaging for Internal Users in Odoo
                Restrict Chatter Send Option Odoo User Settings
                Odoo User-Level Chatter Control
                Role-Based Chatter Message Control in Odoo
                Hide Send Message Button Based on User Access Rights
                Per Model Send Message Control Odoo
                Custom Model Chatter Button Hide Odoo
                
    """,
    "depends": ["web", "mail"],
    "data": [
        "views/res_users_view_inherit.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "show_hide_send_message_button/static/src/xml/chatter_topbar.xml",
        ],
    },
    "images": [
        "static/description/main_screen.gif",
    ],
    "currency": "USD",
    "price": 19.9,
    "application": False,
    "auto_install": False,
    "installable": True,
    "license": "OPL-1",
}
