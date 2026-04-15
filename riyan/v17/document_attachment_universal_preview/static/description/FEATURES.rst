================================================================================
Feature list — Universal Document Attachment Preview (Odoo 18)
================================================================================

SEO keywords: Odoo attachment preview, document preview without download, PDF
preview, Word Excel PowerPoint preview, OpenDocument preview, chatter file
viewer, MS Office online viewer, video attachment preview, Odoo 18 productivity.

--------------------------------------------------------------------------------
Core capabilities
--------------------------------------------------------------------------------

* Preview attachments **inside Odoo** before downloading (saves time and local
  storage).
* Works **everywhere standard mail attachments** use the built-in file viewer
  (chatter on CRM, Sales, Project, Helpdesk, etc.).
* **PDF**: native Odoo PDF.js viewer (unchanged, full quality).
* **Images**: zoom, rotate, pan (standard Odoo viewer).
* **Video and audio**: extended MIME support (e.g. OGG, QuickTime, WAV, WebM)
  where the browser allows playback.

--------------------------------------------------------------------------------
Advanced document preview
--------------------------------------------------------------------------------

* **Microsoft Word** (``.doc``, ``.docx``) and macro-enabled variants.
* **Microsoft Excel** (``.xls``, ``.xlsx``) and **CSV**.
* **Microsoft PowerPoint** (``.ppt``, ``.pptx``).
* **OpenDocument** (``.odt``, ``.ods``, ``.odp``).
* **RTF** documents.
* Embedding via **Microsoft Office Online** or optional **Google Docs viewer**
  (admin choice in Settings).
* **In-viewer controls** for Office: zoom in, zoom out, reset, mouse wheel zoom,
  **open in new tab** for difficult cases.

--------------------------------------------------------------------------------
Configuration & compliance
--------------------------------------------------------------------------------

* Settings under **Discuss** for enabling or disabling online Office preview
  and choosing Google vs Microsoft embed.
* Clear **web.base.url** guidance for public HTTPS (required for online Office
  / Google rendering).

--------------------------------------------------------------------------------
Technical
--------------------------------------------------------------------------------

* Odoo **18.0** compatible, **OWL** / **web.assets_backend** integration.
* Extends mail **Attachment** model client-side and **FileViewer** UI without
  replacing core modules.
