============================================================
Document Directory Manager — Step-by-step configuration
============================================================

**Full walkthrough (field-by-field, roles, checklists):** see
``CONFIGURATION_STEP_BY_STEP.rst`` in this folder.

Prerequisites
-------------
* Odoo 18.0
* Install module **Document Directory Manager — Folders, Tags, Security & Sequences**
  (technical name: ``document_directory_tags_security``).

Step 1 — Assign security groups
--------------------------------
#. Open **Settings → Users & Companies → Users**.
#. Open a user who should administer the library → tab **Access Rights**.
#. Under category **Document Directory Hub**, assign **one** primary profile:

   * **Document Manager** — full directories, all documents, tag configuration, security.
   * **Document User** — only directories explicitly assigned on each folder; cannot create tags.
   * **Document Employee (My Documents)** — only the **Document → My Documents** menu and attachments they **own**.

.. note::
   Avoid giving the same person **Document Employee** together with **Document Manager** unless you intentionally want merged record rules (broader access).

Step 2 — Create directory tags (optional)
-------------------------------------------
#. **Document → Configuration → Directory Tags**.
#. Create labels (e.g. *Finance*, *HR*, *Sales*) and colors.
#. Use them on directory forms for classification.

Step 3 — Create document tags (optional)
----------------------------------------
#. **Document → Configuration → Document Tags**.
#. Create labels used on individual files (e.g. *Contract*, *Draft*, *Signed*).
#. **Document Users** may **apply** these tags but cannot create or edit tag records.

Step 4 — Create directories
----------------------------
#. **Document → Directories** (kanban or list).
#. Set **Name**, **Parent Directory** (for a tree), and optionally **Related Model**:

   * When **Related Model** is set (e.g. *Sales Order*), new chatter attachments on that model are **auto-filed** into this directory when no folder was chosen manually.
#. **Sequence prefix / padding** — each directory owns an ``ir.sequence``; new attachments filed here receive a **Document Reference** (e.g. ``DOC/00001``). Adjust **Sequence prefix** for folder-specific codes (e.g. ``SO/%(range_year)s/`` if your ``ir.sequence`` supports it).
#. **Security** tab:

   * **Restrict to Groups** — empty = no extra group filter; if set, the user must belong to **at least one** listed group.
   * **Assigned Document Users** — users in the **Document User** group only see directories where they appear in this list.

Step 5 — Verify roles
---------------------
* Log in as **Document User**: confirm only **assigned** directories appear and **All Documents** respects record rules.
* Log in as **Document Employee**: confirm only **My Documents** is useful and other attachments are hidden.

Step 6 — Optional integrations
------------------------------
* **Universal preview** — works well alongside ``document_attachment_universal_preview`` for in-browser viewing.
* **Smart buttons on business documents** — add a standard button with ``res_model`` / ``res_id`` domain on ``ir.attachment`` filtered by the current record (example in your custom module).

Troubleshooting
---------------
* **No sequence number** — open the directory form and ensure **Numbering Sequence** exists (created automatically); use **developer mode** if needed.
* **Document User sees no folders** — add the user under **Assigned Document Users** and ensure **Restrict to Groups** (if any) matches the user’s groups.
* **Employees cannot open a file** — check **Owner** on the attachment; employees are limited by the **Owner** field and the “My Documents” filter uses ``owner_id``.
