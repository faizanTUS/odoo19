# Discuss & Chat Access Control — configuration guide

This module turns **Discuss**, the **messaging systray**, and **chat pop-ups** off for everyone until you allow specific users.

---

## Step 1 — Install the module

1. Enable **Developer Mode** (optional but helpful).
2. Go to **Apps**, remove the **Apps** filter, search for **Discuss & Chat Access Control**.
3. Click **Activate** (Install).

**Important:** After installation, **no user** has Discuss/chat UI by default — including administrators. Plan to enable at least one admin (see step 3) so someone can manage the system comfortably.

---

## Step 2 — Understand the security group

- **Group name:** **Discuss & live chat** (technical XML id: `hide_user_discussion.group_discussion_enabled`).
- **Category:** **Discuss access** (appears under user **Access Rights**).
- **Default:** The group is **not** assigned to any user automatically.

Users **with** this group: see the **Discuss** app, the **chat/mail icon** in the top bar, and **floating chat windows**.

Users **without** it: those elements stay hidden (backend web client).

---

## Step 3 — Allow a user (recommended: toggle on user form)

1. Go to **Settings** → **Users & Companies** → **Users**.
2. Open the user.
3. Open the **Preferences** tab.
4. In the **Discuss** section (only visible to **Administrator** / **Access Rights** managers: `Settings` admins), turn **Enable discussion** **on**.
5. Save.
6. Ask the user to **refresh the browser** (F5 or Ctrl+R) so the web client loads the updated session.

**Alternative:** On the **Access Rights** tab, add the group **Discuss & live chat** to **Inherited groups** (same effect).

---

## Step 4 — First admin after install

If you locked yourself out of Discuss as the only admin:

1. Stay logged in as **administrator**.
2. Open your own user (**Settings** → **Users** → your user).
3. Enable **Enable discussion** (or assign **Discuss & live chat** on **Access Rights**).
4. Save and refresh the browser.

---

## Step 5 — Verify

As a user **without** the group:

- **Discuss** should not appear in the app switcher.
- The **messaging** icon should not appear in the systray.
- **Chat bubbles / pop-ups** should not appear.

As a user **with** the group, the above should work as in standard Odoo.

---

## Limitations (good to know)

- **Direct URLs:** A user without access might still open a Discuss-related client action if they know the exact URL. This module focuses on **normal UI** (menu, systray, chat hub). Tight server-side restrictions on Discuss models would be a separate hardening step.
- **Chatter** on documents (log / messages on forms) is **not** removed by this module; it only targets **Discuss app**, **systray messaging**, and **chat hub** windows.
- **Portal / website** frontends are not the main target of the backend assets; behavior there depends on your installed apps.

---

## Uninstall

If you uninstall the module, restore standard Odoo behavior by updating apps and ensuring menus and assets reload. Re-assign standard **Discuss** access through normal groups if you customized them.

---

## Technical reference

| Piece | Role |
|--------|------|
| `security/discussion_security.xml` | Defines **Discuss & live chat** group |
| `views/mail_menu_views.xml` | Restricts **Discuss** root menu to that group |
| `models/ir_http.py` | Adds `discussion_enabled` to `session_info` for the web client |
| `models/res_users.py` | **Enable discussion** toggle ↔ group membership |
| `static/src/js/discussion_feature_boot.js` | Removes systray item; patches **ChatHub** |
| `static/src/xml/chat_hub_discussion.xml` | Hides chat hub unless `discussion_enabled` |

Module technical name: **`hide_user_discussion`**.
