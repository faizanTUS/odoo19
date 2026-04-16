# Global Search Pro for Odoo - Multi-Model Search &amp; User Access Control

Modern and efficient Global Search for Odoo. Search across multiple models from one place, with grouped results, keyboard navigation, recent searches, and record images.

## Features

- **One-click search box** – Open a search box from the top bar (magnifying glass icon) to search any record.
- **Grouped results by type** – Results are grouped by model description (e.g. Contacts, Sale Orders, Journal Entries).
- **Keyboard friendly** – Use **↑** / **↓** to move, **Enter** to open the selected result, **Escape** to close.
- **Recent searches** – Recent search terms are stored in the browser and shown when the search box is empty.
- **Clean, modern & mobile responsive** – Simple layout that works on desktop and mobile.
- **Model filtering** – Only models with **Has Mail Thread** and **Has Mail Activity** are searched (relevance and performance).
- **Display name search** – Search uses the `display_name` field for natural results.
- **Record images** – When available, record images (`image_1920`) are shown (e.g. contacts, products).

## Installation

### 1. Place the module

Ensure the module is on the addons path used by your Odoo instance:

- Either copy the `tus_smart_global_search` folder into your custom addons directory (e.g. `project/` or `addons/`).
- Or ensure your `addons_path` in the Odoo config includes the directory that contains `tus_smart_global_search`.

Example `odoo.conf`:

```ini
[options]
addons_path = /path/to/odoo/addons,/path/to/enterprise,/path/to/project
```

Where `tus_smart_global_search` is at `/path/to/project/tus_smart_global_search`.

### 2. Update the app list

- Go to **Apps**.
- Remove the "Apps" filter (if applied).
- Click **Update Apps List** (if you don’t see the module).
- Search for **Global Search Pro for Odoo - Multi-Model Search &amp; User Access Control**.

### 3. Install the module

- Open the **Global Search Pro for Odoo - Multi-Model Search &amp; User Access Control** module card.
- Click **Install**.

No extra configuration is required. The search icon appears in the top bar (systray) for all backend users.

## Configuration and setup

### No configuration required

- **Which models are searched?**  
  All models that have both **Has Mail Thread** and **Has Mail Activity** (as defined in **Settings → Technical → Database Structure → Models**). You don’t need to configure this; it uses Odoo’s standard flags.

### Optional: restrict or extend searchable models

- Go to **Settings → Technical → Database Structure → Models**.
- For a model to appear in Global Search it must have:
  - **Has Mail Thread** = true  
  - **Has Mail Activity** = true  
- Only custom/editable models allow changing these flags; standard models are already set by their modules (e.g. `mail`, `crm`, `sale`).

### Recent searches

- Stored in the browser’s **local storage** under the key `global_search_recent` (last 10 terms).
- No server or company configuration. Each browser/device has its own list.
- Clearing site data or using a private window will clear recent searches.

### Permissions

- Only **logged-in backend users** can use Global Search.
- Results are filtered by **record access rights**: users only see records they can read.
- No extra security groups; if a user can open a record from the menu, they can open it from Global Search.

## Usage

1. **Open the search**  
   Click the **magnifying glass** icon in the top bar (next to the user menu).

2. **Type to search**  
   Enter at least 2 characters. Results appear grouped by type (Contacts, Sale Orders, etc.).

3. **Choose a result**  
   - **Mouse:** Click a row to open the form.  
   - **Keyboard:** Use **↑** / **↓** to move the highlight, then **Enter** to open.

4. **Recent searches**  
   When the input is empty, the panel shows recent search terms. Click one or select with keyboard and press **Enter** to run it again.

5. **Close**  
   Click outside the panel or press **Escape**.

## Technical notes

- **Backend:** JSON route `/tus_smart_global_search/search` (auth `user`). Searches `ir.model` for models with `is_mail_thread` and `is_mail_activity`, then searches `display_name` with `ilike` and returns grouped results (with optional `image_1920` info).
- **Frontend:** OWL component in the systray; popover with input, grouped list, keyboard handling, and recent searches from `localStorage`.
- **Dependencies:** `web`, `mail` (for `ir.model` mail flags).
