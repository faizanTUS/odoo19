# Advanced Access Control Pro — Step-by-step guide (Odoo 18)

**Module technical name:** `advanced_access_control`  
**Product title (SEO):** Advanced Access Control Pro — Granular Security & UI Rules for Odoo 18

This guide walks you from installation through common configuration patterns. It also includes keywords useful for
internal documentation or marketplace listings (Odoo 18, access rights manager, field-level security, hide menus,
read-only users, export control).

---

## Step 1 — Add the module to your addons path

1. Copy or clone the folder `advanced_access_control` into an addons directory that your Odoo 18 server already loads (
   for example `project/` next to your other custom modules).
2. Ensure the **addons path** includes that directory (configuration file `addons_path` or the `-s` / `--addons-path`
   CLI option).

---

## Step 2 — Install the module

1. Enable **Developer mode** (Settings → scroll to bottom → Activate the developer mode), or start Odoo with a user that
   can install apps.
2. Go to **Apps**, remove the *Apps* filter, search for **Advanced Access Control Pro** (or the technical name above).
3. Click **Install**.

Dependencies: **base**, **web**, **mail** (mail is required for chatter-related UI integration).

---

## Step 3 — Open the configuration menu and who may edit policies

1. With Developer mode on, open **Settings → Technical → Advanced Access Control** (the **Technical** menu is tied to
   *Developer mode* / technical features).
2. **Who can open and edit policy records** (the forms under *Policies* and *Audit log*) is controlled by Odoo access
   rights on this module’s models:
    - Users in **Settings / Administrator** — the group **Access Rights** / **Settings** (`base.group_system`) have *
      *read, write, create, and unlink** on all advanced-access models (see `security/ir.model.access.csv`). After
      installing or upgrading this module, **`base.group_system` also implies** **Advanced Access Control — Manager**,
      so you do not need to tick that extra group for full Settings admins (it still appears under **Customizations**
      for delegated policy admins who are *not* full Settings users).
    - Users who have **only** **Advanced Access Control — Manager** (without Settings) get the same CRUD on policy
      models; they still need a way to open **Technical** menus if policies live there.
3. **If you see** “You are not allowed to modify `advanced.access.policy`…” **only users in Manager or Settings may edit
   policies** — that is Odoo’s normal ACL message. Common causes: you are logged in as a user **without** those groups (
   e.g. **Marc Demo**), or access rows were not applied. **Upgrade the module** (`-u advanced_access_control`) so
   `security/ir.model.access.csv` and group data reload; on a **new install**, `post_init_hook` also repairs missing ACL
   links. Then **log out and log in** (or restart the server) so group and ACL caches refresh.
4. **Important distinction:** “Full rights on **policy configuration**” does **not** mean those users ignore active
   policies. If an administrator is listed on a policy (or in a targeted group), **advanced rules can still apply** to
   them in normal use. In code, rules are skipped for the **superuser** user (`SUPERUSER_ID`, usually the same as the
   default *Administrator* login) and whenever `env.su` is used—those paths bypass this module’s checks. Any other user
   with `base.group_system` is **not** automatically exempt from policies.
5. **Policy name vs Sales app:** A policy can be named “sale Order” and have lines for model **Sales Order** — that only
   describes what the policy does. **Access errors on the policy form** refer to model **`advanced.access.policy`**, not
   `sale.order`. If **Marc Demo** cannot create quotations, check the policy’s **Model access** tab (**Allow Create** on
   Sales Order), not the policy’s name.

---

## Step 4 — Create your first policy

1. Open **Policies** → **Create**.
2. Set **Name** (e.g. “Sales — hide cost fields”).
3. Under **Apply to**, add at least one **user** or **group** (required for active policies).
4. Save.

---

## Step 5 — Global options (read-only, chatter, debug)

| Option                             | Effect                                                                                                                                                                                                                                                        |
|------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Global read-only (UI + server)** | Disables create/edit/delete on the client (form/list attributes) and blocks `create`, `write`, and `unlink` in the ORM for most models. A small **whitelist** still allows mail/bus traffic and this module’s own models so the UI does not break completely. |
| **Hide chatter**                   | For affected users, form layouts skip the mail chatter (OWL patch on the form renderer).                                                                                                                                                                      |
| **Disable developer / debug mode** | After each request, `debug` is cleared from the session so developer mode does not stay active for that user.                                                                                                                                                 |
| **Audit denials**                  | When a rule from this module denies an operation, a line can be written to **Audit log** (see Step 9).                                                                                                                                                        |

**Tip:** Combine **Global read-only** with normal Odoo groups so users still have menu access but cannot mutate data.

---

## Step 6 — Model access (CRUD, export, duplicate, domain)

On the **Model access** tab, add lines with:

- **Model** — target model (e.g. `sale.order`).
- **Allow** checkboxes for **read / create / write / unlink / export / duplicate**.
- **Unlink:** Unchecking blocks delete in this module and in the UI. Checking **does not override** Odoo’s own access
  rights: e.g. **Sales / User** has no unlink on `sale.order`, so the delete action stays hidden until Odoo grants it (
  e.g. **Sales / Manager**).
- **Export:** When unchecked, the list **Export** action is hidden and server export is blocked, even if the user has
  the **Access to export feature** group.
- **Duplicate:** Requires **Allow create** (duplicate creates a new record). If **Allow create** is off, duplicate is
  treated as off in the UI and on the server.
- **Record domain** (optional, advanced) — a **Python literal** domain, e.g. `[('state', '=', 'draft')]`. If set, that
  line’s *denials* apply only to records matching the domain. If empty, the line applies to the whole model.

**Semantics:** If **any** line for the same model denies an operation for a given record (or denies create with no
per-record scope), access is denied. Multiple lines are intended for advanced combinations; start with **one line per
model** until you are comfortable with interactions.

---

## Step 7 — Field modifiers (invisible / readonly / required + conditions)

On **Field modifiers**:

- Choose **Model** and enter the **technical field name**.
- **Modifier:** invisible, read-only, or required.
- **When (expression)** (optional): a client-side expression like `state == 'done'` (same family as dynamic view
  attributes in Odoo 18). If empty, the modifier is always applied (`1`).

The server injects attributes into the loaded view **architecture** for that user, so standard Odoo view inheritance
still applies first.

---

## Step 8 — Menus, buttons, and notebook pages

- **Hidden menus:** pick `ir.ui.menu` records. Those menus (and their children in the loaded menu tree) disappear for
  affected users via the standard menu blacklist hook.
- **Hidden buttons:** set **Model** and the button **`name`** attribute from the form/list XML (e.g. `action_confirm`).
- **Hidden notebook pages:** set **Model** and the page **`string`** exactly as in the view (case-sensitive).

After changing policies, users may need a **full refresh** (F5) so menus and assets reload.

---

## Step 9 — Audit log

1. Enable **Audit denials** on the policy.
2. Open **Technical → Advanced Access Control → Audit log** to review entries (user, model, operation, short detail).

---

## Step 10 — Performance and caching

Rules are cached per user (`ormcache` on `uid`). After you **create, edit, or delete** a policy or line, the registry
cache is cleared so changes apply on the next request.

---

## Step 11 — Troubleshooting

| Symptom                    | What to check                                                                                                                                                      |
|----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Nothing changes for a user | User must be in **Users** or **Groups** on an **active** policy; confirm the user is not `sudo` / superuser (rules are skipped for superuser mode).                |
| Menu still visible         | Correct menu item selected? Clear cache / hard refresh; menu data is hashed in the session.                                                                        |
| Button still visible       | Confirm the XML `name` of the button; some actions use `type="object"` with different names.                                                                       |
| Field still editable       | Another view or studio customization may override modifiers; check effective view priority.                                                                        |
| Export still possible      | **Export** is enforced in `export_data` / `fields_get` for rules without a domain; domain-scoped export rules are enforced when exported records match the domain. |

---

## Step 12 — Security disclaimer

This module is powerful. Only trusted administrators should manage policies. Field expressions and domains are not a
substitute for proper **record rules** and **access rights** for high-security separation—use them together with
standard Odoo security for defense in depth.

---

## Quick reference — Files in this module

| Path                                | Role                                                             |
|-------------------------------------|------------------------------------------------------------------|
| `models/advanced_access_policy.py`  | Policy and line models                                           |
| `models/advanced_access_service.py` | Rule aggregation and cache                                       |
| `models/models_base.py`             | `get_view`, `_check_access`, `copy`, `export_data`, `fields_get` |
| `models/ir_ui_menu.py`              | Menu blacklist                                                   |
| `models/ir_http.py`                 | Session flags + debug clearing                                   |
| `static/src/js/*.js`                | Global read-only (form) + hide chatter                           |
| `security/`                         | Groups and access CSV                                            |
| `views/`                            | UI and menus                                                     |

---

*Last updated for Odoo **18.0**.*
