================================================================================
Document Directory Manager — Detailed step-by-step configuration
================================================================================

.. contents:: Table of contents
   :local:
   :depth: 2

This guide matches module **document_directory_tags_security** (display name:
*Document Directory Manager — Folders, Tags, Security & Sequences*) for **Odoo 18**.

--------------------------------------------------------------------------------
Part A — Install the module
--------------------------------------------------------------------------------

A.1 Enable developer mode (recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Go to **Settings**.
#. Scroll to the bottom and enable **Activate the developer mode** (or use the
   debug URL your instance uses).

*Why:* Easier to see technical fields (e.g. **Numbering Sequence**) when troubleshooting.

A.2 Add the addon path
~~~~~~~~~~~~~~~~~~~~~~

#. Ensure the folder ``document_directory_tags_security`` is on your Odoo
   **addons path** (e.g. ``extra-addons``).
#. Restart the Odoo service if you changed the path.

A.3 Install
~~~~~~~~~~~

#. Open **Apps**.
#. Remove the **Apps** filter so you see all modules.
#. Search for **Document Directory Manager** or **document_directory_tags_security**.
#. Click **Activate** / **Install**.
#. Wait until the installation finishes with no error in the log.

A.4 After install (automatic)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The module creates:

* Security groups under category **Document Directory Hub**.
* A default global sequence with code ``document.hub.default`` (prefix ``DOC/``).
* New fields on **Attachments** (**Directory**, **Document Tags**, **Owner**,
  **Document Reference**, etc.).
* A **post-install** SQL step that sets **Owner** from **Created by** on old
  attachments where Owner was empty.

--------------------------------------------------------------------------------
Part B — Understand the three roles
--------------------------------------------------------------------------------

Use **Settings → Users & Companies → Users → [user] → Access Rights**.
Find section **Document Directory Hub**.

.. list-table::
   :widths: 28 72
   :header-rows: 1

   * - Group
     - Typical use
   * - **Document Manager**
     - Administrators / records officers: full library setup and all menus.
   * - **Document User**
     - Staff who work only in folders where they are explicitly assigned.
   * - **Document Employee (My Documents)**
     - **My Documents** menu; attachments where **Owner** = that user.

B.1 Document Manager — step by step
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Open the user form.
#. Under **Document Directory Hub**, enable **Document Manager** only (remove
   Document User / Document Employee from this user if they were set by mistake).
#. **Save**.

**Capabilities:**

* Menu **Document** → **Directories**, **Directory Structure**, **All Documents**,
  **Configuration** (both tag menus), **My Documents**.
* Create, edit, archive directories.
* Create and edit **Directory Tags** and **Document Tags**.
* Set **Restrict to Groups** and **Assigned Document Users** on directories.
* See all attachments allowed by standard Odoo rights (record rules for this
  module do not restrict the manager).

B.2 Document User — step by step
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Open the user form.
#. Enable **Document User** under **Document Directory Hub**.
#. **Do not** enable **Document Employee** on the same user unless you understand
   that record rules combine (usually you pick one “document” role).
#. **Save**.

**Capabilities:**

* Menus: **Directories**, **Directory Structure**, **All Documents**, **My Documents**.
* **No** **Document → Configuration** (only managers).
* Sees **only directories** where that user is listed in **Assigned Document Users**
  on the directory form **and** passes **Restrict to Groups** (if any).
* Sees attachments that are either **unfiled** (no directory) or filed in a
  directory the user is allowed to see.
* Can **apply** existing **Document Tags** on attachments; cannot create new tag
  definitions.

**Important:** A Document User who is not assigned on any directory will see
**no directories** in the directory menus and may see only “unfiled” attachments
under **All Documents**.

B.3 Document Employee (My Documents) — step by step
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Open the user form.
#. Enable **Document Employee (My Documents)**.
#. **Save**.

**Capabilities:**

* Menu **Document** → **My Documents** (and the **Document** app root).
* **No** **Directories**, **Directory Structure**, **All Documents**, or
  **Configuration**.
* Sees only ``ir.attachment`` records whose **Owner** is that user (record rule).

**Important:** New uploads from chatter get **Owner** defaulting to the current
user. Legacy files may need Owner corrected by a manager (or rely on the
post-install backfill from **Created by**).

--------------------------------------------------------------------------------
Part C — Configure tags (optional but recommended)
--------------------------------------------------------------------------------

C.1 Directory tags
~~~~~~~~~~~~~~~~~~

#. Log in as a **Document Manager**.
#. Go to **Document → Configuration → Directory Tags**.
#. Click **New**.
#. Set **Name** (e.g. ``Finance``, ``HR``, ``Sales``).
#. Optionally set **Color** (color picker).
#. **Save**.
#. Repeat for each folder category you want to filter or report on.

**Usage:** On each **Directory** form, tab **Directory Tags**, add tags to
classify the folder (not the individual file).

C.2 Document tags
~~~~~~~~~~~~~~~~~

#. **Document → Configuration → Document Tags**.
#. **New** → **Name** (e.g. ``Signed``, ``Draft``, ``Invoice``) → optional **Color**
   → **Save**.

**Usage:** On an **Attachment** form (or list/kanban where available), **Document
Users** and **Managers** can set **Document Tags**. **Document Users** cannot
open the configuration menus to create new tag records.

--------------------------------------------------------------------------------
Part D — Create and tune directories
--------------------------------------------------------------------------------

D.1 Open the directory screen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. **Document → Directories**.
#. Use **Kanban** (folder cards) or switch to **List** for bulk editing.

D.2 Create a root folder
~~~~~~~~~~~~~~~~~~~~~~~~

#. Click **New** (or **Create**).
#. **Name**: e.g. ``Sales Orders``.
#. **Parent Directory**: leave empty for a root folder.
#. **Active**: checked.
#. **Sequence**: lower numbers sort first in lists (e.g. ``10``).

D.3 Optional — subfolders
~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Create another directory.
#. Set **Parent Directory** to the root you created.
#. **Save**.

You can also use the **Sub-Directories** tab on the parent form and add lines
there (company defaults apply from the parent where relevant).

D.4 Optional — link to an Odoo model (auto-filing)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Field: Related Model**

#. On the directory form, set **Related Model** (technical model list from
   ``ir.model``), e.g. *Sales Order* (``sale.order``).
#. **Save**.

**Effect:** When a new attachment is created **without** a stored binary field
(``res_field`` empty) and **without** a directory already set, the system searches
for an **active** directory whose **Related Model** matches the attachment’s
``res_model`` and **Company** matches (or directory company is empty). The first
match by **Sequence**, then **Id**, wins.

**If no directory matches:** the attachment still gets a **Document Reference**
from the **global** ``DOC/`` sequence (not from a folder sequence).

D.5 Numbering — Sequence prefix and padding
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Fields:** **Sequence prefix**, **Sequence padding**

#. **Sequence padding**: number of digits (e.g. ``4`` → ``0001``).
#. **Sequence prefix**: stored on the technical ``ir.sequence`` as **Prefix**.
   You can use a static prefix like ``SO/`` or formats supported by Odoo’s
   sequence engine (depending on version/settings).

After save, the module creates or updates a dedicated **Numbering Sequence**
(visible with developer mode). New attachments filed in this directory receive
**Document Reference** from that sequence.

**Rebuild (advanced):** If you change prefix/padding and numbers look wrong, a
manager can use the object method **action_rebuild_sequence** from server
actions / Studio — or ask a developer; the form does not expose a button by
default.

D.6 Security tab — Restrict to Groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Field: Restrict to Groups**

* **Empty:** No **extra** group check at the directory level (users still need a
  valid **Document** role: Manager / User / Employee).
* **Non-empty:** The user must belong to **at least one** of the listed **Access
  Groups** to use that directory together with the **Document User** assignment
  rules.

**Example:**

* Add group **Sales / User: Own Documents Only** to **Restrict to Groups**.
* Only users in that group (who are also assigned as Document Users on this
  folder) see the folder and its filed attachments.

D.7 Security tab — Assigned Document Users
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Field: Assigned Document Users**

* List every **Document User** who must see **this** directory.
* Users with **only** **Document Manager** do not need to be listed here.

**Typical workflow:**

#. Create directory ``Contracts``.
#. Add internal users **Alice** and **Bob** (both have **Document User**).
#. **Save**.

Alice and Bob now see ``Contracts`` in directory menus (subject to **Restrict to
Groups**). Other Document Users do not.

D.8 Company (multi-company)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Field: Company**

* Set the directory’s company when you use **multi-company**.
* Auto-filing matches directories where ``company_id`` is empty **or** equals
  the attachment’s company context.

--------------------------------------------------------------------------------
Part E — Work with attachments
--------------------------------------------------------------------------------

E.1 All Documents (Manager / Document User)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. **Document → All Documents**.
#. Use **Kanban** or **List**.
#. **Managers/Users:** left **search panel** (if visible) filters by **Directory**
   and **Document Tags**.
#. Search bar: filters such as **Has directory**, **Unfiled**, **My documents
   (owner)** (owner = **Owner** field).

E.2 My Documents
~~~~~~~~~~~~~~~~

#. **Document → My Documents**.
#. Default filter **My documents (owner)** uses **Owner = current user**.

E.3 From chatter
~~~~~~~~~~~~~~~~

#. On a business document (e.g. quotation), attach a file as usual.
#. If a directory matches **Related Model**, the attachment may be auto-filed.
#. Open the attachment (from the attachment list / Documents app) to set
   **Directory**, **Document Tags**, or **Owner** manually if needed.

--------------------------------------------------------------------------------
Part F — Verification checklist
--------------------------------------------------------------------------------

Use three browser sessions (or private windows) with three test users.

F.1 Document Manager checklist
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[ ] Can open **Configuration → Directory Tags** and **Document Tags**.

[ ] Can create a directory and see **Security** and **Directory Tags** tabs.

[ ] **All Documents** lists attachments as expected.

[ ] **Directory Structure** opens and groups/filters work.

F.2 Document User checklist
~~~~~~~~~~~~~~~~~~~~~~~~~~~

[ ] **Configuration** menus are **missing**.

[ ] After assignment on a directory, that directory appears; unassigned ones do
    **not**.

[ ] **All Documents** does not show other users’ restricted folders’ content beyond
    the module rules.

F.3 Document Employee checklist
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[ ] Only **My Documents** is practical under **Document**.

[ ] Cannot open **Directories** or **All Documents**.

[ ] Only attachments with **Owner = self** appear.

--------------------------------------------------------------------------------
Part G — Troubleshooting (expanded)
--------------------------------------------------------------------------------

G.1 “Document User sees zero directories”
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Log in as **Document Manager**.
#. Open the directory → **Security** → **Assigned Document Users** → add the user.
#. If **Restrict to Groups** is set, confirm the user is in one of those groups.

G.2 “No Document Reference on new file”
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Check if the attachment is a **stored binary field** (``res_field`` set). Those
   are **skipped** by design for numbering.
#. Open the directory → confirm a **Numbering Sequence** exists (developer mode).

G.3 “Employee cannot see a file they uploaded”
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Open the attachment → **Owner** must be that user.
#. If **Owner** is wrong, a **Document Manager** can fix it on the attachment form.

G.4 “Search panel missing”
~~~~~~~~~~~~~~~~~~~~~~~~~~

The attachment **search panel** is limited to **Document Manager** and **Document
User** (not **Document Employee**).

--------------------------------------------------------------------------------
Part H — Reference — Menus vs roles
--------------------------------------------------------------------------------

+----------------------+----------+------+-----------+
| Menu                 | Manager  | User | Employee  |
+======================+==========+======+===========+
| Document (app)       | Yes      | Yes  | Yes       |
+----------------------+----------+------+-----------+
| Directories          | Yes      | Yes  | No        |
+----------------------+----------+------+-----------+
| Directory Structure  | Yes      | Yes  | No        |
+----------------------+----------+------+-----------+
| All Documents        | Yes      | Yes  | No        |
+----------------------+----------+------+-----------+
| Configuration/*      | Yes      | No   | No        |
+----------------------+----------+------+-----------+
| My Documents         | Yes      | Yes  | Yes       |
+----------------------+----------+------+-----------+

--------------------------------------------------------------------------------
End of document
--------------------------------------------------------------------------------

For a shorter overview, see ``CONFIGURATION.rst`` in the same folder.
