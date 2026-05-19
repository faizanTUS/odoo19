================================================================================
Universal Document Attachment Preview — Configuration (Odoo 18)
================================================================================

This document explains how to install the module and configure attachment
preview for PDF, Microsoft Office, OpenDocument, images, video, and audio.

For a strictly numbered walkthrough, see ``STEP_BY_STEP_CONFIGURATION.rst`` in
this folder.

--------------------------------------------------------------------------------
1. Installation
--------------------------------------------------------------------------------

#. Copy the module folder ``document_attachment_universal_preview`` into an
   addons directory that is listed in your Odoo ``addons_path`` (for example
   ``extra-addons/``).
#. Restart the Odoo server.
#. Enable developer mode (optional but useful).
#. Open **Apps**, remove the *Apps* filter, search for **Universal Document
   Attachment Preview**.
#. Click **Activate** (Install).

--------------------------------------------------------------------------------
2. Base URL (required for Office / Google online preview)
--------------------------------------------------------------------------------

Microsoft Office Online and Google Docs viewers fetch your file from a **full
URL** built from **web.base.url** plus ``/web/content/...`` (and access tokens
when applicable).

#. Go to **Settings → Technical → Parameters → System Parameters**.
#. Locate **web.base.url**.
#. Set it to the **public HTTPS URL** of your Odoo instance (for example
   ``https://erp.mycompany.com``), not ``http://localhost`` or a private IP, if
   you want online Office preview to work.

If the URL is not reachable from the internet (or from Microsoft/Google
viewer infrastructure), the iframe may stay blank; users can still use
**Download** or **Open in new tab** from the preview toolbar.

--------------------------------------------------------------------------------
3. Discuss / Mail settings
--------------------------------------------------------------------------------

#. Go to **Settings**.
#. Open the **Discuss** section (mail settings).
#. **Universal attachment preview — Microsoft Office**: keep enabled to allow
   Word, Excel, PowerPoint, CSV, RTF, and OpenDocument preview in the file
   viewer.
#. **Use Google Docs viewer instead of Microsoft**: enable only if your
   organization allows sending document URLs to Google and Microsoft’s viewer
   does not work in your region; this **replaces** the Office Online embed with
   Google’s embedded viewer (not a runtime fallback).

After changing toggles, click **Save**.

--------------------------------------------------------------------------------
4. Usage
--------------------------------------------------------------------------------

#. Open any form that uses **chatter** (e.g. Sales Order, CRM Lead, Project task).
#. Attach or open an existing attachment.
#. Click the attachment preview (same flow as for PDF or images in standard Odoo).
#. For Office documents, use the bottom toolbar: zoom in/out, reset zoom,
   **open in new tab** if the embed fails.

Keyboard shortcuts in the viewer (Office): ``+`` / ``-`` / ``0`` (reset zoom),
same idea as for images where applicable.

--------------------------------------------------------------------------------
5. Privacy and security notes
--------------------------------------------------------------------------------

* Online preview sends a **direct link to the file** to Microsoft or Google so
  their service can render it. Assess compliance (GDPR, confidentiality) before
  enabling this on databases with sensitive documents.
* **access_token** on attachments is included in URLs when Odoo provides it;
  protect tokens and use HTTPS.

--------------------------------------------------------------------------------
6. Troubleshooting
--------------------------------------------------------------------------------

* **Blank Office preview**: Check **web.base.url**, HTTPS, firewall, and that
  the attachment is not still uploading.
* **Video/audio not playing**: Confirm the MIME type is correct; some formats
  depend on browser support.
* **Discuss voice messages**: Voice attachments stay non-previewable (same as
  standard Odoo Discuss behavior).
