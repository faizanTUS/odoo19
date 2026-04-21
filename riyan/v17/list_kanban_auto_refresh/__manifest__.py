# -*- coding: utf-8 -*-
{
    "name": "List & Kanban Auto Refresh — Soft Live Data Reload",
    "summary": "Auto-refresh list and kanban views without full page reload: configurable interval, global defaults in General Settings, per-view toggle, visibility-aware timers.",
    "description": """
List & Kanban Auto Refresh for Odoo 17
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
Odoo 17, list view refresh, kanban refresh, auto reload, soft refresh, live data, interval refresh, tree view, real-time board, productivity, General Settings.
    """,
    "version": "17.0.1.0.0",
    "category": "Productivity/Interface",
    "author": "Custom",
    "website": "https://www.odoo.com",
    "license": "LGPL-3",
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
    "installable": True,
    "application": False,
    "auto_install": False,
}
