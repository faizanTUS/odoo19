================================================================================
Many2Many Attachment Preview — Step-by-step configuration (Odoo 18)
================================================================================

This guide covers installation, ``web.base.url``, Discuss settings, and how to
add preview-enabled attachment fields to your own models.

--------------------------------------------------------------------------------
1. Install the module
--------------------------------------------------------------------------------

#. Place the module under your addons tree. In this workspace the canonical
   path is ``odoo18/project/tus_many2many_attachment_preview/`` — add the parent
   folder ``project/`` to ``addons_path`` (not only the module directory).
#. Restart the Odoo server process.
#. Enable **Developer mode** (optional, useful for technical menus).
#. Open **Apps**, clear the *Apps* filter, search for **Many2Many Attachment
   Preview** (or the technical name ``tus_many2many_attachment_preview``).
#. Click **Activate**.

**Note:** Do not install together with another module that patches the same
mail ``Attachment`` / ``FileViewer`` behavior twice. If you use
``document_attachment_universal_preview``, choose one module or merge their
features manually.

--------------------------------------------------------------------------------
2. Server / addons path
--------------------------------------------------------------------------------

Example ``odoo.conf``::

    [options]
    addons_path = /path/to/odoo/addons,/path/to/odoo18/project

Ensure the ``project`` directory is on the path so Odoo finds the
``tus_many2many_attachment_preview`` folder inside it.

Step-by-step instructions for operators: see ``STEP_BY_STEP_CONFIGURATION.md``
in the module root.

--------------------------------------------------------------------------------
3. Public URL for Office / Google online preview (advanced)
--------------------------------------------------------------------------------

Word, Excel, PowerPoint, and similar files are shown inside an iframe using
**Microsoft Office Online** or **Google Docs viewer**. Those services download
your file from a **public HTTPS URL** built from Odoo’s **web.base.url**.

#. Go to **Settings → Technical → Parameters → System Parameters**.
#. Find **web.base.url**.
#. Set it to the canonical HTTPS URL of your site (e.g.
   ``https://erp.example.com``), not ``http://127.0.0.1``, if you need online
   Office preview in production.

If the URL is not reachable from the internet, the iframe may stay blank; users
can still **Download** or use **Open in new tab** on the Office toolbar inside
the viewer.

--------------------------------------------------------------------------------
4. Discuss / Settings toggles
--------------------------------------------------------------------------------

#. Open **Settings** (admin).
#. In the **Discuss** section, find:

   * **Attachment preview: Microsoft Office online** — enables Office documents
     in the file viewer (chatter and many2many preview).
   * **Use Google Docs viewer for Office files** — replaces the Microsoft embed
     with Google’s viewer (only if your policy allows sending file URLs to
     Google).

#. Click **Save**.

--------------------------------------------------------------------------------
5. Use on custom models (many2many attachments)
--------------------------------------------------------------------------------

**Python** (your model)::

    attachment_ids = fields.Many2many(
        "ir.attachment",
        "your_model_attachment_rel",
        "model_id",
        "attachment_id",
        string="Attachments",
    )

**XML** (form view)::

    <field name="attachment_ids" widget="many2many_binary"/>

After installing this module, each row shows the usual download/remove controls
plus a **Preview** (eye) icon when the file type supports in-browser preview
(PDF, images, common video types, and Office when online preview is enabled).

Optional widget options (standard Odoo) still apply, for example::

    <field
        name="attachment_ids"
        widget="many2many_binary"
        options="{'accepted_file_extensions': 'image/png,image/jpeg,application/pdf', 'number_of_files': 5}"
    />

**Built-in example**
^^^^^^^^^^^^^^^^^^^^

* Model ``map2.attachment.example`` with one ``attachment_ids`` field and
  ``many2many_binary`` widget.
* Menu: **Discuss → Configuration → Attachment preview example** (all internal users).

--------------------------------------------------------------------------------
6. Chatter “Files”
--------------------------------------------------------------------------------

No extra configuration: attachments in the composer and in messages use the same
**FileViewer** with extended video MIME types and optional Office embedding.

--------------------------------------------------------------------------------
7. Privacy and security
--------------------------------------------------------------------------------

* Online Office / Google preview exposes a **direct URL** to the attachment
  (including ``access_token`` when present). Review GDPR / confidentiality
  before enabling on sensitive databases.
* Always prefer **HTTPS** for **web.base.url** in production.

--------------------------------------------------------------------------------
8. Troubleshooting
--------------------------------------------------------------------------------

* **Eye icon missing:** The file type may not be previewable (e.g. unknown
  binary). Use Download.
* **Blank Office preview:** Check **web.base.url**, firewall, and HTTPS.
* **Module not in Apps list:** Update apps list; confirm ``addons_path``.
