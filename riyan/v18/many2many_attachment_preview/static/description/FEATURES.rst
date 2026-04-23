================================================================================
Feature list — Many2Many Attachment Preview (Odoo 18) — App Store SEO
================================================================================

**Keywords:** Odoo 18 attachment preview, many2many attachment viewer, PDF image
video preview, document preview without download, Word Excel PowerPoint online
viewer, chatter file preview, ir.attachment many2many_binary, productivity
module, enterprise document workflow.

--------------------------------------------------------------------------------
Core features
--------------------------------------------------------------------------------

* **In-browser preview** for attachments linked on **many2many_binary** fields
  (eye icon per file).
* **Same modal viewer** as standard Odoo **chatter** (Download, navigation
  between previewable files, keyboard shortcuts).
* **PDF** — built-in PDF.js viewer.
* **Images** — zoom, pan, rotate, print (standard FileViewer).
* **Video / audio** — HTML5 playback for common types (MP4, WebM, OGG,
  QuickTime, etc., subject to browser support).

--------------------------------------------------------------------------------
Advanced features
--------------------------------------------------------------------------------

* **Microsoft Office** — DOC/DOCX, XLS/XLSX, PPT/PPTX, CSV, RTF, OpenDocument;
  embedded via **Office Online** or optional **Google Docs viewer** (admin
  setting).
* **Office viewer controls** — zoom in/out (mouse wheel and keyboard), reset,
  open embed in a new browser tab.
* **Extra MIME types** for video/audio on mail **Attachment** objects (chatter
  cards).

--------------------------------------------------------------------------------
Configuration
--------------------------------------------------------------------------------

* **Settings → Discuss:** toggles for Office online preview and Google Docs
  viewer.
* **System parameter web.base.url:** must be a correct **HTTPS** public URL for
  online Office/Google preview to fetch files.

--------------------------------------------------------------------------------
Developer-friendly
--------------------------------------------------------------------------------

* Add to any model::

      attachment_ids = fields.Many2many("ir.attachment", ...)

* In the form view::

      <field name="attachment_ids" widget="many2many_binary"/>

* Standard **options** still work: ``accepted_file_extensions``,
  ``number_of_files``.

--------------------------------------------------------------------------------
Compliance note
--------------------------------------------------------------------------------

Online viewers receive a URL to the file; assess **data protection** policies
before enabling Office/Google preview on confidential data.
