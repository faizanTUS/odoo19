# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    "name": "Auto Refresh List & Kanban Views | Real-Time Data Reload",
    "version": "18.0.0.0",
    "category": "Productivity/Interface",
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    "summary": """Auto-refresh list and kanban views without full page reload: configurable interval, global defaults in General Settings, per-view toggle, visibility-aware timers.
        
    tus
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited 
    list
    kanban
    refresh
    refresh list
    refresh kanban
    reload
    view
    data
    record
    without refresh
    sync
    reflect
    auto refresh list view
    auto refresh kanban view
    real time data refresh
    live data reload
    dynamic view refresh
    auto reload backend data
    real time record update
    live sync data
    auto refresh records
    background data refresh
    instant data update
    live backend refresh
    refresh without reload
    auto refresh interface
    real time list update
    real time kanban update
    auto refresh system
    dynamic data update
    auto refresh module
    live data monitoring
    automatic record refresh
    auto refresh dashboard
    real time system updates
    auto refresh UI
    background refresh odoo
    list view auto reload
    kanban auto reload
    real time business data
    auto update records
    live record sync
    data refresh automation
    smart auto refresh
    auto refresh configuration
    real time refresh tool
    dynamic backend refresh
    auto refresh solution
    live update system
    instant refresh module
    auto refresh feature
    real time UI update
    auto refresh functionality
    live system data
    auto refresh backend
    real time data sync
    auto refresh list data
    kanban refresh automation
    auto refresh records module
    dynamic record refresh
    real time tracking data
    auto refresh performance
    live business updates
    auto refresh integration
    automatic data reload
    real time data visibility
    auto refresh optimization
    auto refresh control
    auto refresh toggle
    auto refresh settings
    live update feature
    auto refresh enhancement
    real time monitoring tool
    auto refresh enterprise
    auto refresh productivity
    auto refresh workflow
    real time collaboration data
    auto refresh usability
    auto refresh experience
    auto refresh solution module
    auto refresh improvement
    auto refresh performance tool
    auto refresh system module
    real time backend solution
    
    """,
    "description": """
Auto Refresh List & Kanban Views | Real-Time Data Reload for Odoo 18
======================================

Keep **tree (list)** and **kanban** views up to date with **soft reloads** (data refresh only — no browser hard refresh).

**Highlights**
--------------
* **General Settings** defaults: enable/disable globally, default interval in milliseconds (min **1000**). When the global switch is **off**, auto refresh is **disallowed** everywhere and the toolbar control is disabled.
* **Per-view toolbar** toggle when globally allowed: pause or resume for the current screen only; a new list/kanban instance resets to the global default (refresh **on** if the global switch is on).
* **Smarter refresh**: pauses while the browser tab is hidden; avoids overlapping loads; skips list auto-refresh while a row is in **edit mode**.

**Ideal for**
-------------
Live dashboards, support queues, manufacturing boards, CRM pipelines, helpdesk teams, and any workflow where records change often.

**Keywords (SEO)**
------------------
Odoo 18, list view refresh, kanban refresh, auto reload, soft refresh, live data, interval refresh, tree view, real-time board, productivity, General Settings.


    tus
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited
    list
    kanban
    refresh
    refresh list
    refresh kanban
    reload
    view
    data
    record
    without refresh
    sync
    reflect
    auto refresh list view
    auto refresh kanban view
    real time data refresh
    live data reload
    dynamic view refresh
    auto reload backend data
    real time record update
    live sync data
    auto refresh records
    background data refresh
    instant data update
    live backend refresh
    refresh without reload
    auto refresh interface
    real time list update
    real time kanban update
    auto refresh system
    dynamic data update
    auto refresh module
    live data monitoring
    automatic record refresh
    auto refresh dashboard
    real time system updates
    auto refresh UI
    background refresh odoo
    list view auto reload
    kanban auto reload
    real time business data
    auto update records
    live record sync
    data refresh automation
    smart auto refresh
    auto refresh configuration
    real time refresh tool
    dynamic backend refresh
    auto refresh solution
    live update system
    instant refresh module
    auto refresh feature
    real time UI update
    auto refresh functionality
    live system data
    auto refresh backend
    real time data sync
    auto refresh list data
    kanban refresh automation
    auto refresh records module
    dynamic record refresh
    real time tracking data
    auto refresh performance
    live business updates
    auto refresh integration
    automatic data reload
    real time data visibility
    auto refresh optimization
    auto refresh control
    auto refresh toggle
    auto refresh settings
    live update feature
    auto refresh enhancement
    real time monitoring tool
    auto refresh enterprise
    auto refresh productivity
    auto refresh workflow
    real time collaboration data
    auto refresh usability
    auto refresh experience
    auto refresh solution module
    auto refresh improvement
    auto refresh performance tool
    auto refresh system module
    real time backend solution
    """,
    "depends": ["web", "base_setup"],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "list_kanban_auto_refresh/static/src/xml/list_kanban_auto_refresh.xml",
            "list_kanban_auto_refresh/static/src/js/list_kanban_auto_refresh.js",
        ],
    },
    'images': [
        'static/description/main_screen.gif'
    ],
    'price': 15.00,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
