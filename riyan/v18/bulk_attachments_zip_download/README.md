# Bulk Attachment ZIP Downloader | Mass Download Files & Documents(Odoo 18)

SEO-oriented technical name: **`bulk_attachments_zip_download`**.  
Display name: **Bulk Attachment ZIP Downloader | Mass Download Files & Documents— Mass Documents CRM Sales HR**.

## What it does

From any **list view**, select one or more records, open **Actions**, choose **Download all files**, review the preview table, then **Download**. Attachments are packed into a single ZIP named like `sale.order_attachments.zip` (technical model name + `_attachments.zip`).

## Step-by-step configuration

### 1. Install the module

1. Copy the folder `bulk_attachments_zip_download` into your Odoo **addons** path (e.g. `extra-addons/`).
2. Restart the Odoo server.
3. Enable **Developer mode** (optional but useful).
4. **Apps** → **Update Apps List**.
5. Remove the **Apps** filter, search **Bulk Attachments ZIP** (or the technical name).
6. Click **Install**.

### 2. Use it (end users)

1. Open a **list view** (e.g. Sales → Quotations, CRM → Leads, Project → Tasks).
2. Tick one or more rows (or use domain selection if your list supports it).
3. Click **Actions** (in the selection bar) → **Download all files**.
4. In the wizard, optionally toggle **Include chatter attachments** and click **Refresh list** if needed.
5. Remove any lines you do not want in the ZIP (optional).
6. Click **Download**. Your browser receives `{model}_attachments.zip`.

### 3. Administrator settings

Go to **Settings** → **General Settings** and find the block **Bulk attachment ZIP**:

| Setting | Purpose |
|--------|---------|
| **Include chatter attachments by default** | Default value of the wizard checkbox. |
| **Maximum files per ZIP** | `0` = no limit. Otherwise blocks oversized exports. |
| **Maximum total size (MB)** | `0` = no limit. Compares sum of attachment sizes before building the ZIP. |

System parameters (alternative): `bulk_attachments_zip.include_chatter`, `bulk_attachments_zip.max_files`, `bulk_attachments_zip.max_total_mb`.

### 4. Hide the action on specific list views (advanced)

On the related `ir.actions.act_window`, add to **Context**:

```python
{'disable_bulk_attachment_zip': True}
```

## Dependencies

- `web` — list view **Actions** integration.
- `mail` — chatter / `mail.message`–linked attachments when the option is enabled.
- `base_setup` — settings form block.

## Files for Odoo App Store

- **`FEATURES.rst`** — bullet features and SEO phrases for long descriptions.
- **`static/description/index.html`** — short HTML landing text (add your screenshots and `icon.png`).

## Adding store assets

Place in `static/description/`:

- `icon.png` (recommended 128×128)
- Screenshots (PNG) referenced from `index.html`
- Optional `banner.png` — if you add it, you can reference it from `__manifest__.py` under `"images"`.

## Support & customization

Typical extensions: extra domains for attachments, filters by MIME type, or scheduled cleanup of transient wizards (Odoo already vacuums transients).
