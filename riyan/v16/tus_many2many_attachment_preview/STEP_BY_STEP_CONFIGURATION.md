# Smart Attachment Preview Pro with File Size Viewer | Chatter & Many2many Binary Viewer | PDF, Image, Video & Office Viewer — Step-by-Step Configuration (Odoo 16)

Module location (this repository):

`odoo16/project/tus_many2many_attachment_preview/`

Follow the steps **in order**.

---

## Step 1: Add the module to Odoo’s addons path

1. Confirm the module folder exists on disk, for example:  
   `/home/tus/workspace/odoo16/project/tus_many2many_attachment_preview/`
2. Open your Odoo configuration file (e.g. `odoo.conf`).
3. Locate **`addons_path`**. Add the **`project`** directory (the parent folder that contains `tus_many2many_attachment_preview`), **not** only the module folder.

   Example:

   ```ini
   [options]
   addons_path = /home/tus/workspace/odoo16/odoo/addons,/home/tus/workspace/odoo16/project
   ```

   Adjust paths to match your server. The important part is that **`.../odoo16/project`** is listed so Odoo can discover **`tus_many2many_attachment_preview`** inside it.

4. Save the configuration file.
5. **Restart the Odoo service** (required after changing `addons_path`).

---

## Step 2: Update the Apps list

1. Log in as a user with **Settings / Administration** access.
2. Open **Apps**.
3. Enable **Developer mode** if you use it for technical menus (optional).
4. Open the **Apps** menu action menu (⋮) and choose **Update Apps List**, or use **Settings → Apps → Update Apps List** depending on your build.
5. Confirm **Update** when prompted.

---

## Step 3: Install the module

1. In **Apps**, remove the **Apps** filter so **All** modules are visible.
2. Search for **Many2Many Attachment Preview** (technical name: `tus_many2many_attachment_preview`).
3. Click **Activate** / **Install**.
4. Wait until installation completes without errors.

**Conflict note:** Do not install this alongside another addon that patches the same mail **Attachment** / **FileViewer** behavior (for example `document_attachment_universal_preview`) unless you have merged the code—double patches can break the UI.

---

## Step 4: Set `web.base.url` (required for Office / Google document preview)

Online preview for Word, Excel, PowerPoint, etc. uses Microsoft or Google services that fetch the file from a **public URL** derived from Odoo’s base URL.

1. Go to **Settings → Technical → Parameters → System Parameters** (Developer mode may be required).
2. Open **`web.base.url`**.
3. Set **Value** to your real site URL, preferably **HTTPS**, e.g. `https://erp.yourcompany.com`.
4. Avoid `http://localhost` or private IPs for production if you need Office embed to work from the internet.
5. Save.

If this URL is wrong or unreachable from the internet, Office preview may show a blank iframe; users can still **Download** or use **Open in new tab** in the viewer toolbar when available.

---

## Step 5: Configure Discuss / attachment preview toggles

1. Go to **Settings** (main settings app).
2. Scroll to the **Discuss** block.
3. Configure:
   - **Attachment preview: Microsoft Office online** — enable or disable embedding of Office documents in the file viewer (chatter + many2many preview).
   - **Use Google Docs viewer for Office files** — only enable if your security policy allows sending document URLs to Google; this uses Google’s embed instead of Microsoft’s.
4. Click **Save**.

---

## Step 6: Use many2many attachments on your own models

### 6.0 Built-in example (try the preview immediately)

After installing this module:

1. Open **Discuss** → **Configuration** → **Attachment preview example**.
2. Create a record, upload a file, click the **eye** icon to preview.

Technical model: **`map2.attachment.example`** (see `models/attachment_preview_example.py` and `views/attachment_preview_example_views.xml`).

### 6.1 Python model

Define a many2many to `ir.attachment` in **your** module (or copy from the built-in example). Use a **unique** relation table name in your database.

```python
attachment_ids = fields.Many2many(
    comodel_name="ir.attachment",
    relation="your_model_attachment_rel",
    column1="model_id",
    column2="attachment_id",
    string="Attachments",
)
```

(You can also use the older positional form: `fields.Many2many("ir.attachment", "rel", "col1", "col2", string="Attachments")`.)

### 6.2 Form view XML

Use the standard binary widget (this module adds the **Preview** eye icon):

```xml
<field name="attachment_ids" widget="many2many_binary"/>
```

### 6.3 Optional widget options (standard Odoo)

```xml
<field
    name="attachment_ids"
    widget="many2many_binary"
    options="{'accepted_file_extensions': 'image/png,image/jpeg,application/pdf', 'number_of_files': 5}"
/>
```

### 6.4 Upgrade your addon

After changing Python or XML in **your** module, **upgrade** that module (**Apps → your module → Upgrade**, or `-u your_module_name`) so the model and views load.

### 6.5 Example: `sale.order` (ready-made addon)

If you use **Sales**, you can install the companion module **`sale_order_attachment_preview`** in the same `project/` folder. It adds `order_attachment_ids` and `order_attachment_limited_ids` on **sale.order** with a tab **Order documents**. See its `README.md`.

---

## Step 7: Verify behavior

1. Use **Discuss → Configuration → Attachment preview example**, or open any form that uses **`many2many_binary`** on a `Many2many('ir.attachment')` field.
2. Upload or open a **PDF** or **PNG**: a **Preview** (eye) icon should appear for supported types; click it to open the full-screen viewer.
3. On a record with **chatter**, attach a file and open preview from the attachment card—the same viewer should be used.
4. Test an **Office** file only if Step 4 is satisfied and Step 5 allows Office preview.

---

## Step 8: Troubleshooting

| Symptom | What to check |
|--------|----------------|
| Module does not appear in Apps | `addons_path` includes `.../project`, server restarted, **Update Apps List** run. |
| No eye icon on a file | Type may not be previewable (unknown binary); use **Download**. |
| Blank Office preview | **`web.base.url`**, HTTPS, firewall, and external access to `/web/content/...`. |
| Error when clicking the eye | Hard-refresh assets / upgrade `tus_many2many_attachment_preview`; avoid duplicate **FileViewer** patches from another module. |
| JavaScript errors after install | Another module may also patch **FileViewer** / **Attachment**; resolve duplicate addons. |

---

## Further reading

- **`doc/CONFIGURATION.rst`** — same topics in reStructuredText.
- **`static/description/DESCRIPTION.rst`**, **`static/description/FEATURES.rst`** — App Store–oriented text.
