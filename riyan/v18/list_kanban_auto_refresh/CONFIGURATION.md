# List & Kanban Auto Refresh — step-by-step configuration

Use this guide after installing **`list_kanban_auto_refresh`** on **Odoo 18**.

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
3. Open another menu or another view type, then return to list/kanban: behaviour resets to the **global default** (on if the global switch is on and you have not changed code; each mount starts from session defaults).

## 4. Advanced behaviour (summary)

- **Tab hidden:** reload is skipped until the tab is visible again.
- **List inline edit:** reload is skipped while a row is being edited.
- **Concurrent loads:** a new tick does not start if the previous reload is still running.
- **Global switch off:** no automatic refresh; the **Auto Refresh** button is **disabled** with a tooltip pointing to General Settings.
