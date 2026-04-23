================================================================================
Many2Many Attachment Preview — PDF, Image, Video & Office (Odoo 18)
================================================================================

**Odoo attachment preview**, **many2many binary preview**, **PDF viewer**,
**image preview**, **MP4 / video preview**, **Word Excel PowerPoint preview**,
**preview without download**, **ir.attachment**, **chatter files**, **Odoo 18**
**productivity**, **document management**.

--------------------------------------------------------------------------------
What this module does
--------------------------------------------------------------------------------

Save **time** and **local disk space**: users open **PDF**, **images**,
**video**, and (optionally) **Microsoft Office** documents **inside Odoo**
before deciding to download them.

* **Many2many** fields with ``widget="many2many_binary"`` automatically show a
  **Preview** (eye) button for supported files, using the same full-screen
  viewer as **mail / chatter** attachments.
* **Discuss** attachment cards keep **extended preview** (more video/audio MIME
  types + Office online embed when configured).

--------------------------------------------------------------------------------
Business value
--------------------------------------------------------------------------------

* Fewer mistaken downloads and less clutter on user devices.
* Faster validation of invoices, contracts, screenshots, and recordings
  attached to CRM, projects, helpdesk, or custom apps.
* One consistent preview experience across **chatter** and **form** attachment
  lists.

--------------------------------------------------------------------------------
Technical highlights (advanced)
--------------------------------------------------------------------------------

* **Odoo 18** OWL assets: patches **Many2ManyBinaryField**, mail **Attachment**,
  and **FileViewer** (no fork of ``web`` or ``mail``).
* Loads **access_token** and **checksum** for correct ``/web/content`` URLs.
* **Settings** under Discuss: enable/disable Office online preview; optional
  **Google Docs** viewer instead of Microsoft.
* **Office toolbar** in the viewer: zoom, reset, **open in new tab**.

For installation and ``web.base.url`` setup, see **doc/CONFIGURATION.rst** in
the module source.
