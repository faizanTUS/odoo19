# User Based Product Attribute Restrictions | Advanced Product Attribute Security – Step-by-Step Setup & Verification

Follow these steps in order. After each step, check the "You should see" line to confirm it worked.

---

## Part A: Install and Upgrade Module

### Step 1: Put the module in the addons path

1. Ensure the folder `product_attribute_restriction` is in an addons path Odoo uses (e.g. `addons`, `custom_addons`, or `project`).
2. If you added it while Odoo was running, restart the Odoo server.

**You should see:** No error when Odoo starts.

---

### Step 2: Install or upgrade the module

1. Log in as **Administrator** (or a user with **Apps** access).
2. Go to **Apps**.
3. Remove the **Apps** filter if needed (click the search bar and clear filters).
4. In the search box, type: **User Based Product Attribute Restrictions | Advanced Product Attribute Security**.
5. If you see the module with an **Install** button → click **Install**.
6. If you see the module with an **Upgrade** button → click **Upgrade** (recommended after code changes).
7. Wait until the page reloads and the module shows as installed.

**You should see:** The app **User Based Product Attribute Restrictions | Advanced Product Attribute Security** is installed (no Install button, or "Upgrade" available).

---

### Step 3: Confirm the Products app is installed

1. In **Apps**, search for **Products** (or **Products & Pricelists**).
2. It must be **Installed**. If not, install it first (User Based Product Attribute Restrictions | Advanced Product Attribute Security depends on it).

**You should see:** Products app is installed.

---

## Part B: Configure Users (Admin / Full Access)

### Step 4: Give yourself (admin) full attribute access

1. Go to **Settings** (gear icon).
2. Open **Users & Companies** → **Users**.
3. Open the **Administrator** user (or the user you use for configuration).
4. Go to the **Access Rights** tab.
5. Scroll until you see a section named **Product Attributes** (from this module).
6. In that section, find the checkbox **Manage Product Attributes**.
7. **Check** the box **Manage Product Attributes**.
8. Click **Save**.

**You should see:** Under **Product Attributes**, the option **Manage Product Attributes** is checked, and below it a field **Allowed Product Attributes** may be visible (it is ignored when the checkbox is checked).

---

## Part C: Create a Test Restricted User (Optional but Recommended)

### Step 5: Create a test user (no Manage Product Attributes)

1. **Settings** → **Users & Companies** → **Users**.
2. Click **New**.
3. Fill in:
   - **Name:** e.g. `Test Restricted`
   - **Email:** e.g. `test.restricted@example.com`
   - **Password:** set a password you will use to log in as this user.
4. Open the **Access Rights** tab.
5. Ensure the user has access to products (e.g. **Sales** → **User: All Documents** or **Product Creation** / **Product: Administrator** so they can open and edit products). Without product edit rights, they cannot add attribute lines.
6. In the **Product Attributes** section:
   - **Leave** the checkbox **Manage Product Attributes** **unchecked**.
7. In **Allowed Product Attributes** (many2many field below):
   - Click the field and add **one** attribute only, e.g. **Size** (if you don’t have attributes yet, create them first – see Step 6).
8. Click **Save**.

**You should see:** User saved; **Manage Product Attributes** is unchecked; **Allowed Product Attributes** contains exactly one attribute (e.g. Size).

---

### Step 6: Ensure product attributes exist (if needed)

1. Go to **Sales** → **Products** → **Configuration** → **Attributes** (or **Settings** → **Products** → **Attributes** depending on your menu).
2. You should have at least two attributes, e.g. **Size** and **Color**.
3. If not, create them: **New**, set name (e.g. Size, Color), save.

**You should see:** At least **Size** and **Color** (or two different attributes) in the list.

---

## Part D: Test the Restriction (with logging)

### Step 7: Turn on Odoo server log level (to see the step-by-step log)

1. Restart Odoo with log level **INFO** (or **DEBUG** if you want more detail).
   - Example: `odoo-bin -c odoo.conf --log-level=info`
   - Or set in your config: `log_level = info`
2. Keep the terminal/server log visible so you can see lines containing `[User Based Product Attribute Restrictions | Advanced Product Attribute Security]`.

**You should see:** When you add an attribute to a product, log lines like:
- `[User Based Product Attribute Restrictions | Advanced Product Attribute Security] user=... attribute=... has_manage_group=... allowed_count=...`
- Then either `ALLOWED (...)` or `DENIED (...)`.

---

### Step 8: Test as Administrator (should always be allowed)

1. Log in as **Administrator** (or a user with **Manage Product Attributes** checked).
2. Go to **Sales** → **Products**.
3. Open any product (or create a new one) that has **Attributes & Variants** (e.g. a storable product).
4. Open the **Attributes & Variants** tab.
5. Add a new line: choose any **Attribute** (e.g. Color) and at least one **Values**, then save (or click outside the line).
6. Check the **server log**: you should see something like:
   - `[User Based Product Attribute Restrictions | Advanced Product Attribute Security] user=admin ... has_manage_group=True ...`
   - `[User Based Product Attribute Restrictions | Advanced Product Attribute Security] ALLOWED (user has Manage Product Attributes)`
7. The line should save without error.

**You should see:** Attribute line is saved; in the log, `has_manage_group=True` and **ALLOWED**.

---

### Step 9: Test as restricted user – allowed attribute (should work)

1. Log out and log in as the **test restricted user** (e.g. Test Restricted) from Step 5.
2. Go to **Sales** → **Products** → open a product (or create one).
3. Open the **Attributes & Variants** tab.
4. Add a new line with the attribute that is in this user’s **Allowed Product Attributes** (e.g. **Size**) and select at least one value, then save.
5. Check the **server log**. You should see something like:
   - `[User Based Product Attribute Restrictions | Advanced Product Attribute Security] user=test.restricted ... has_manage_group=False allowed_count=1 ...`
   - `[User Based Product Attribute Restrictions | Advanced Product Attribute Security] ALLOWED (attribute in user allowed list)`
6. The line should save without error.

**You should see:** Attribute line is saved; in the log, **ALLOWED (attribute in user allowed list)**.

---

### Step 10: Test as restricted user – forbidden attribute (should block)

1. Still logged in as the **test restricted user**.
2. On the same (or another) product, go to **Attributes & Variants**.
3. Add a **new** line and choose an attribute that is **not** in this user’s allowed list (e.g. **Color** if only **Size** was allowed).
4. Select at least one value and try to save (e.g. click outside the line or click Save).
5. Check the **server log**. You should see something like:
   - `[User Based Product Attribute Restrictions | Advanced Product Attribute Security] user=... has_manage_group=False ...`
   - `[User Based Product Attribute Restrictions | Advanced Product Attribute Security] DENIED for user=... attribute=Color`
6. In the browser you should see an error popup:  
   **"User Based Product Attribute Restrictions | Advanced Product Attribute Security: You are not allowed to add the attribute '...' to products. Contact your administrator..."**
7. The new attribute line should **not** be saved.

**You should see:** Error message in the UI and **DENIED** in the log; the forbidden attribute line is not created.

---

## Part E: Quick Checklist If It Still Doesn’t Work

- [ ] **Module state:** Apps → **User Based Product Attribute Restrictions | Advanced Product Attribute Security** is **Installed** (or upgraded after code change).
- [ ] **Products app:** **Products** (Products & Pricelists) is installed.
- [ ] **User form:** **Settings** → **Users** → **Access Rights** tab shows the **Product Attributes** section and the **Manage Product Attributes** checkbox and **Allowed Product Attributes** field.
- [ ] **Restricted user:** For the test user, **Manage Product Attributes** is **unchecked** and **Allowed Product Attributes** contains only the attributes you want to allow (e.g. only Size).
- [ ] **Product rights:** The restricted user can open and edit products (e.g. has Sales + product write/create rights) so the **Attributes & Variants** tab is visible and editable.
- [ ] **Log:** Server restarted with `log_level=info` (or `debug`) and you look for `[User Based Product Attribute Restrictions | Advanced Product Attribute Security]` when adding an attribute line.
- [ ] **No log at all:** If you add an attribute but see **no** `[User Based Product Attribute Restrictions | Advanced Product Attribute Security]` line, the code path may not be hit (e.g. different way of saving). In that case, try adding the attribute from the product form **Attributes & Variants** tab as in Steps 8–10.

---

## Admin access and Create/Edit Attribute (Search: Attribute modal)

- **Admin (or user with “Manage Product Attributes”)**: In the product form, **Attributes & Variants** tab, when you add a line and open the **Search: Attribute** modal you can:
  - Use **New** to create a new product attribute.
  - Click an attribute to open and edit it.
- **Restricted user (no “Manage Product Attributes”)**: In the same **Search: Attribute** modal:
  - The **New** button is hidden and the attribute form cannot be opened (**no_create**, **no_open**).
  - If they could trigger create/edit (e.g. from another screen), the server would block it with: *"You are not allowed to create or edit Product Attributes..."* (and the same for Attribute Values).

So: only users with **Manage Product Attributes** (e.g. Mitchell Admin in your setup) can create or edit attributes from that modal; others only select from existing attributes (and only those in their allowed list when adding to a product).

---

## Summary: What the log lines mean

| Log line | Meaning |
|----------|--------|
| `has_manage_group=True` | User has **Manage Product Attributes** → no restriction. |
| `has_manage_group=False` | User is restricted; allowed list is used. |
| `allowed_count=N allowed_ids=[...]` | User has N allowed attributes (IDs in the list). |
| `ALLOWED (user has Manage Product Attributes)` | User is admin/full access. |
| `ALLOWED (attribute in user allowed list)` | User is restricted but this attribute is in their list. |
| `DENIED for user=... attribute=...` | User is restricted and this attribute is not allowed → error shown in UI. |

Following this order and checking the log after each test will show exactly at which step the restriction runs and whether it allows or denies the operation.
