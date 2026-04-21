# List & Kanban Auto Refresh — step-by-step configuration

Use this guide after installing **`list_kanban_auto_refresh`** on **Odoo 19**.

## 1. Install the module

1. Optional: enable **Developer Mode** (Settings → scroll down → Developer Tools).
2. Open **Apps**, clear the *Apps* filter, search for **List & Kanban Auto Refresh** or the technical name **`list_kanban_auto_refresh`**.
3. Click **Activate** / **Install**.

## 2. Global defaults — Settings → General Settings

1. Go to **Settings** (admin / settings rights).
2. Open the **General Settings** screen.
3. Scroll to **Auto Refresh — List & Kanban**.

| Field | Meaning |
|--------|---------|
| **Allow auto refresh data** | **Off** (default): auto refresh is **not allowed** anywhere; the toolbar control is disabled. **On**: list and kanban views may auto-refresh; each new list/kanban screen starts with refresh **on** until the user pauses it from the toolbar. |
| **Refresh interval (ms)** | Time between soft data reloads. **Default: 10000**. **Minimum: 1000** (enforced in Settings and on the server). |

4. Click **Save**.

**Session note:** Interval and the global switch are read when the web session is built. After changing values, ask users to **refresh the browser** (F5) so the client picks up new defaults.

## 3. Per-view toolbar (list & kanban only)

1. Open any **List** (tree) or **Kanban** view.
2. In the control panel (near the cog menu), use **Auto Refresh**:
   - **Blue** = refresh **on** for this view instance.
   - **Grey** = refresh **paused** for this view instance.
3. When global auto refresh is **off**, the button is **disabled** (tooltip explains how to enable it in Settings).

## 4. Upgrade from Odoo 18

If you migrate a database from Odoo 18 with this module already installed, install the **19.0** version of the module on the same `addons_path` and run **Apps → Upgrade** (or `-u list_kanban_auto_refresh`). System parameters `list_kanban_auto_refresh.enabled` and `list_kanban_auto_refresh.interval_ms` are preserved.
