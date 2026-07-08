# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'RingCentral Integration',
    'version': '18.0.1.0.0',
    'category': 'Communications',
    'summary': """RingCentral Integration for Odoo 19 - Calls, History, Transcripts, and CTI
                RingCentral Odoo integration
            Odoo RingCentral connector
            RingCentral Odoo module
            Odoo CTI integration RingCentral
            Odoo VOIP integration RingCentral
            Odoo phone integration RingCentral
            integrate RingCentral with Odoo
            RingCentral telephony inside Odoo
            click to call RingCentral Odoo
            Odoo CRM RingCentral calling
            RingCentral softphone widget in Odoo
            log RingCentral calls in Odoo
            sync RingCentral call history to Odoo
            RingCentral inbound call popup in Odoo
            record RingCentral calls in Odoo
            RingCentral KPI dashboard for Odoo
            Odoo click to dial RingCentral
            Odoo contact center with RingCentral
            Odoo sales call tracking RingCentral
            Odoo helpdesk telephony RingCentral
            Odoo call analytics RingCentral
            RingCentral call recording in Odoo
            RingCentral call transcription in Odoo
            Odoo call reporting RingCentral
            Odoo real time call monitoring RingCentral
            RingCentral Odoo app
            RingCentral Odoo marketplace module
            best RingCentral integration for Odoo
            enterprise RingCentral Odoo solution
            Odoo RingCentral plugin for CRM
    
    """,
    'description': """
RingCentral Integration Module
==============================

This module provides comprehensive RingCentral integration for Odoo 19:

Features:
---------
* Self-service configuration for RingCentral credentials
* Incoming and outgoing call management
* Call history with partner linking
* Call transcripts from RingCentral
* Click-to-call from partner records
* CTI features (screen pop, call controls)
* Embedded RingCentral widget
* Dashboard with call analytics
* Call recordings integration
* Webhook support for real-time updates
RingCentral Odoo integration
            Odoo RingCentral connector
            RingCentral Odoo module
            Odoo CTI integration RingCentral
            Odoo VOIP integration RingCentral
            Odoo phone integration RingCentral
            integrate RingCentral with Odoo
            RingCentral telephony inside Odoo
            click to call RingCentral Odoo
            Odoo CRM RingCentral calling
            RingCentral softphone widget in Odoo
            log RingCentral calls in Odoo
            sync RingCentral call history to Odoo
            RingCentral inbound call popup in Odoo
            record RingCentral calls in Odoo
            RingCentral KPI dashboard for Odoo
            Odoo click to dial RingCentral
            Odoo contact center with RingCentral
            Odoo sales call tracking RingCentral
            Odoo helpdesk telephony RingCentral
            Odoo call analytics RingCentral
            RingCentral call recording in Odoo
            RingCentral call transcription in Odoo
            Odoo call reporting RingCentral
            Odoo real time call monitoring RingCentral
            RingCentral Odoo app
            RingCentral Odoo marketplace module
            best RingCentral integration for Odoo
            enterprise RingCentral Odoo solution
            Odoo RingCentral plugin for CRM
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
        'security/ringcentral_access.xml',
        'security/ringcentral_security.xml',
        'data/ringcentral_data.xml',
        'views/ringcentral_config_views.xml',
        'views/ringcentral_call_history_views.xml',
        'views/ringcentral_dashboard_views.xml',
        'views/res_partner_views.xml',
        'views/res_users_views.xml',
        'views/ringcentral_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ringcentral_integration/static/src/css/ringcentral_systray.css',
            'ringcentral_integration/static/src/js/ringcentral_boot.js',
            'ringcentral_integration/static/src/js/ringcentral_widget_helper.js',
            'ringcentral_integration/static/src/js/ringcentral_systray_min.js',
            'ringcentral_integration/static/src/xml/ringcentral_systray_templates.xml',
            'ringcentral_integration/static/src/js/ringcentral_kpi_dashboard.js',
            'ringcentral_integration/static/src/xml/ringcentral_kpi_dashboard_templates.xml',
        ],
    },
    'images': ['static/description/main_screen.gif'],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    'price': 499,
    'currency': 'USD',
}

