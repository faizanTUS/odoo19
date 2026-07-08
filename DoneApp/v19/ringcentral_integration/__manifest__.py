# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'RingCentral Integration',
    'version': '19.0.0.0.2',
    'category': 'Communications',
    'summary': """RingCentral Integration for Odoo 19 - Calls, CTI, Contact Sync, Call History, Recordings, Transcripts, Analytics & Multi-Company Support

RingCentral Odoo integration
Odoo RingCentral connector
RingCentral Odoo module
Odoo CTI integration RingCentral
Odoo VoIP integration RingCentral
Odoo phone integration RingCentral
Integrate RingCentral with Odoo
RingCentral telephony inside Odoo
Click-to-call RingCentral Odoo
Odoo CRM RingCentral calling
RingCentral softphone widget in Odoo
Log RingCentral calls in Odoo
Sync RingCentral call history to Odoo
RingCentral inbound call popup in Odoo
RingCentral outbound call management
RingCentral call recording in Odoo
RingCentral call transcription in Odoo
Real-time RingCentral webhooks
Odoo contact synchronization with RingCentral
Sync Odoo contacts to RingCentral
Sync RingCentral contacts to Odoo
Automatic contact creation and updates
Multi-company RingCentral integration
Multi-user access and permissions
RingCentral KPI dashboard for Odoo
Odoo click-to-dial RingCentral
Odoo contact center with RingCentral
Odoo sales call tracking
Odoo CRM telephony integration
Odoo Helpdesk telephony
Call analytics and reporting
Real-time call monitoring
Call activity in Odoo Chatter
OAuth authentication
Call logs and recordings
Customer communication management
RingCentral Odoo app
RingCentral Odoo marketplace module
Enterprise RingCentral Odoo solution
Best RingCentral integration for Odoo
Business phone system integration
Cloud telephony for Odoo
    """,
    'description': """
RingCentral Integration Module
==============================

This module provides a comprehensive RingCentral integration for Odoo 19, enabling businesses to manage telephony, customer communication, and call operations directly from Odoo with real-time synchronization and enterprise-grade features.

Features:
---------
* Multi-company support
* Multi-user access control and permissions
* Self-service RingCentral account configuration
* Secure OAuth authentication
* Incoming and outgoing call management
* Click-to-call from Contacts, CRM, Sales, Helpdesk, and other Odoo modules
* CTI features including screen pop, answer, hold, mute, transfer, and hang-up controls
* Embedded RingCentral softphone/widget
* Automatic call history synchronization
* Call recordings synchronization
* Call transcripts synchronization
* Real-time webhook support for instant call updates
* Contact synchronization from Odoo to RingCentral
* Contact synchronization from RingCentral to Odoo
* Automatic contact creation and updates
* Call activity logging in Odoo Chatter
* CRM lead and customer integration
* Dashboard with call analytics and KPI reporting
* Missed, answered, rejected, inbound, and outbound call tracking
* Real-time call monitoring
* Scheduled background synchronization using cron jobs
* Multiple RingCentral account support
* Fast, scalable, secure, and production-ready architecture
* Compatible with Odoo 19 Community and Enterprise Editions

Keywords:
---------
RingCentral Odoo Integration
Odoo RingCentral Connector
RingCentral Odoo Module
RingCentral VoIP Integration
Odoo CTI Integration
Odoo Phone Integration
RingCentral Telephony
Click-to-Call
Click-to-Dial
Embedded Softphone
RingCentral Widget
Call History Sync
Call Recording
Call Transcription
Inbound Call Popup
Outbound Call Management
Call Analytics
Call Reporting
Call Dashboard
Real-Time Webhooks
Contact Synchronization
Odoo to RingCentral Contact Sync
RingCentral to Odoo Contact Sync
CRM Telephony Integration
Helpdesk Telephony
Sales Call Tracking
Business Communication
Cloud Telephony
Multi-Company Support
Multi-User Access
OAuth Authentication
Call Monitoring
Customer Communication
Enterprise RingCentral Solution
Odoo Marketplace Module
Best RingCentral Integration for Odoo
    """,
    'author': 'TechUltra Solutions Private Limited',
    'website': 'https://www.techultra.in',
    'support': 'mailto:support@techultra.in',
    'depends': [
        'base',
        'contacts',
        'mail',
        'web',
    ],
    'data': [
        'security/ringcentral_groups.xml',
        'security/ir.model.access.csv',
        'security/ringcentral_security.xml',
        'data/ringcentral_data.xml',
        'data/ringcentral_cron_cleanup.xml',
        'data/mail_message_subtype_data.xml',
        'views/ringcentral_config_views.xml',
        'views/ringcentral_contact_sync_views.xml',
        'views/ringcentral_call_history_views.xml',
        'views/ringcentral_dashboard_views.xml',
        'views/res_partner_views.xml',
        'views/res_users_views.xml',
        'views/ringcentral_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ringcentral_integration/static/src/js/ringcentral_popover_security_patch.js',
            'ringcentral_integration/static/src/css/ringcentral_systray.css',
            'ringcentral_integration/static/src/js/ringcentral_access_service.js',
            'ringcentral_integration/static/src/js/ringcentral_call_service.js',
            'ringcentral_integration/static/src/js/ringcentral_oauth_handler.js',
            'ringcentral_integration/static/src/js/ringcentral_boot_service.js',
            'ringcentral_integration/static/src/js/ringcentral_widget_helper.js',
            'ringcentral_integration/static/src/js/ringcentral_systray_min.js',
            'ringcentral_integration/static/src/components/ringcentral_audio_player/ringcentral_audio_player.js',
            'ringcentral_integration/static/src/components/ringcentral_audio_player/ringcentral_audio_player.xml',
            'ringcentral_integration/static/src/xml/ringcentral_systray_templates.xml',
            'ringcentral_integration/static/src/scss/ringcentral_dashboard.scss',
            'ringcentral_integration/static/src/dashboard/dashboard_utils.js',
            'ringcentral_integration/static/src/dashboard/dashboard_components.js',
            'ringcentral_integration/static/src/dashboard/dashboard_shared.xml',
            'ringcentral_integration/static/src/dashboard/ringcentral_dashboard.xml',
            'ringcentral_integration/static/src/dashboard/ringcentral_dashboard.js',
        ],
    },
    'images': ['static/description/main_screen.gif'],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    'price': 519,
    'currency': 'USD',
}

