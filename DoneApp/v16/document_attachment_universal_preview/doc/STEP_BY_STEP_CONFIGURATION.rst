================================================================================
Universal Document Attachment Preview — Step-by-step configuration (Odoo 18)
================================================================================

Follow these steps in order. Skip steps that do not apply (for example, if you
only need PDF/images/video in the browser and do not use Office online preview).

--------------------------------------------------------------------------------
Step 1 — Put the module on the addons path
--------------------------------------------------------------------------------

1.1. Place the folder ``document_attachment_universal_preview`` in a directory
     that appears in your Odoo ``addons_path`` (same pattern as your other
     custom addons).

1.2. Restart the Odoo service so it rescans addons.

--------------------------------------------------------------------------------
Step 2 — Install the module
--------------------------------------------------------------------------------

2.1. Log in as a user who can install apps (Administrator / Settings).

2.2. Enable **Developer mode** if you want full menus (optional).

2.3. Open **Apps**.

2.4. Remove the *Apps* filter so all modules are visible.

2.5. Search for **Universal Document Attachment Preview** (or
     ``document_attachment_universal_preview``).

2.6. Click **Activate** / **Install**.

2.7. Wait for the installation to finish; refresh the browser if prompted.

--------------------------------------------------------------------------------
Step 3 — Set the public base URL (needed for Office / Google embed)
--------------------------------------------------------------------------------

Online viewers (Microsoft Office Online, Google Docs viewer) load your file via
a URL built from **web.base.url**. If this URL is wrong or not reachable from
the internet, Office-style previews may be blank.

3.1. Go to **Settings**.

3.2. Enable **Developer mode** if the Technical menu is hidden.

3.3. Open **Technical → Parameters → System Parameters**.

3.4. Open the parameter **web.base.url** (create it if missing: key
     ``web.base.url``, value your site URL).

3.5. Set the value to your **real public HTTPS URL**, for example
     ``https://erp.example.com`` (no trailing slash unless your deployment
     requires it—match how users open Odoo).

3.6. Save.

3.7. If you use a reverse proxy or multi-company URLs, confirm that this URL
     matches what external services must use to reach **/web/content/...** links.

--------------------------------------------------------------------------------
Step 4 — Turn preview options on or off in Settings
--------------------------------------------------------------------------------

4.1. Go to **Settings**.

4.2. Find the **Discuss** block (mail / discuss settings).

4.3. **Universal attachment preview — Microsoft Office**

     * Leave **enabled** (default) to preview Word, Excel, PowerPoint, CSV, RTF,
       and OpenDocument files inside the file viewer using Office Online.

     * **Disable** if you do not want Office Online embeds at all (policy or
       air-gapped installs).

4.4. **Use Google Docs viewer instead of Microsoft**

     * Leave **disabled** (default) unless you explicitly want Google’s viewer.

     * **Enable** only if your security policy allows sending document URLs to
       Google and you prefer Google’s embed over Microsoft’s (this switches the
       embed, not a silent fallback).

4.5. Click **Save** at the top of Settings.

--------------------------------------------------------------------------------
Step 5 — (Optional) Verify system parameters
--------------------------------------------------------------------------------

These are normally set by the toggles in Step 4. Use this only for debugging or
automation.

5.1. **Settings → Technical → Parameters → System Parameters**.

5.2. Check:

     * ``document_attachment_universal_preview.office_preview`` — ``True`` or
       ``False`` (Office embed on/off).

     * ``document_attachment_universal_preview.google_viewer_fallback`` —
       ``True`` or ``False`` (Google viewer instead of Microsoft when ``True``).

5.3. After manual edits, **upgrade** the module or at least restart Odoo and
     **log out and log in** so the web client reloads ``session_info``.

--------------------------------------------------------------------------------
Step 6 — Clear browser cache if settings do not apply
--------------------------------------------------------------------------------

6.1. Hard-refresh the backend (Ctrl+F5 / Cmd+Shift+R) or clear site data for
     your Odoo origin.

6.2. Try a private/incognito window to rule out stale assets.

--------------------------------------------------------------------------------
Step 7 — Smoke test
--------------------------------------------------------------------------------

7.1. Open a record with **chatter** (e.g. a quotation, lead, or task).

7.2. Upload a small **PDF** or **image** — preview should work like standard
     Odoo.

7.3. Upload a small **.docx** or **.xlsx** — with Step 3 and Office preview
     enabled, the viewer should show the Office embed or an empty frame if the
     URL is unreachable.

7.4. Use **Open in new tab** or **Download** from the viewer toolbar if the
     embed fails.

--------------------------------------------------------------------------------
Quick reference — What works without internet embeds
--------------------------------------------------------------------------------

* **PDF**, **images**, **video**, and **audio** in the viewer depend mainly on
  the browser and correct MIME types, not on Microsoft/Google.

* **Office / OpenDocument / CSV / RTF** online preview depends on **web.base.url**
  and the **Office** / **Google** settings above.

For privacy notes and more troubleshooting, see ``CONFIGURATION.rst`` in this
same folder.
