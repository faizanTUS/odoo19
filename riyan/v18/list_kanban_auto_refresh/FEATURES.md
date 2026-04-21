# Features — List & Kanban Auto Refresh (Odoo 18)

SEO-oriented feature list for documentation and marketplace copy.

## Core features

- **Soft reload** — Refreshes list/kanban **data** via `model.load()`; no full browser refresh.
- **List (tree) + Kanban** — Same UX on both view types.
- **General Settings** — Global on/off and default interval (milliseconds).
- **Minimum interval 1000 ms** — Enforced in `res.config.settings` and in session payload.
- **Per-view toggle** — Pause or resume for the current screen (resets when navigating away / new view instance).
- **Global kill switch** — When “Allow auto refresh data” is off, automatic refresh is disallowed and the toolbar control is disabled.

## Advanced / quality-of-life

- **Page Visibility API** — No reload while the browser tab is in the background.
- **List edit safety** — Skips reload while a record is in **inline edit** mode.
- **Load de-duplication** — Avoids stacking concurrent `load()` calls from the timer.

## Technical stack

- **Backend:** `res.config.settings` + `ir.config_parameter`; `ir.http.session_info` exposes safe defaults to the web client.
- **Frontend:** OWL patches on `ListController` and `KanbanController`; QWeb template inheritance on `web.ListView` and `web.KanbanView`.

## Keywords (SEO)

Odoo 18, list view auto refresh, kanban auto refresh, tree view reload, soft refresh, live list, live kanban, interval refresh, General Settings, productivity, CRM pipeline refresh, helpdesk queue, manufacturing board, real-time data without websocket.
