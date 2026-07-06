# Advanced Inventory Backdate for Odoo 18

This module provides an advanced solution for backdating stock operations (transfers and moves) in Odoo 18, with mass operations, optional accounting date alignment, and a full audit trail.

---

## What Gets Backdated

When you run **Mass Backdate**, the following are updated to the new date you choose:

| Area | Model | Field(s) updated | When |
|------|--------|-------------------|------|
| **Stock Transfer** | `stock.picking` | `date_done` | Always |
| **Stock Move** | `stock.move` | `date` | Always |
| **Stock Move Line** | `stock.move.line` | `date` | Always (for each move line of the transfer) |
| **Accounting Entry** | `account.move` | `date` | Only if **Recalculate Inventory Valuation** is checked (posted entries linked to the stock move; reconciled lines are skipped) |

Audit fields on the transfer: **Original Date Done**, **Backdated By**, **Backdate Reason**.

---

## Step-by-Step Setup

### Step 1: Install the module

1. Place the `inventory_backdate_advanced` folder in your Odoo addons path (e.g. `project/` or `addons/`).
2. Restart Odoo.
3. Log in as administrator → **Apps** → remove the "Apps" filter → search **Advanced Inventory Backdate**.
4. Click **Install**.

### Step 2: Ensure Inventory and (optional) Invoicing

- **Inventory** app must be installed (the module depends on `stock`).
- For **Accounting Entry** backdate: install **Invoicing** and the **stock_account** bridge so inventory valuation and journal entries exist; the module depends on `stock_account`.

### Step 3: Access and permissions

- The **Mass Backdate** menu is visible to users with **Warehouse Management** (Stock Manager).
- To restrict to specific users only: go to **Settings → Users & Companies → Users** → open the user → under **Other** enable **Inventory Backdate Manager** and remove Stock Manager if you want only Backdate Managers to see the menu (otherwise leave both).

### Step 4: Run a backdate

1. Go to **Inventory → Configuration → Mass Backdate**.
2. **New Date:** Choose the date (and time) to apply.
3. **Reason for Backdate:** Enter a reason (required).
4. **Recalculate Inventory Valuation:** Check this if you want linked **Accounting Entry** dates updated; leave unchecked to update only Stock Transfer, Stock Move, and Stock Move Line.
5. **Transfers Filter Domain:** Enter a domain, e.g. `[('state', '=', 'done')]` (see examples below).
6. Click **Apply Mass Backdate**.

After running, verify:

- **Stock Transfer:** Open the transfer → **Effective Date** = new date; **Original Date Done** / **Backdated By** / **Backdate Reason** show the audit trail.
- **Stock Move:** On the transfer, in the **Operations** tab, each move’s **Date** = new date.
- **Stock Move Line:** In **Detailed Operations**, each line’s **Date** = new date.
- **Accounting Entry:** If you used Recalculate Inventory Valuation, open the related journal entry (from the move or from Accounting); **Date** = new date (unless the entry was reconciled, in which case it is not changed).

---

## Features

| Feature | Description |
|--------|-------------|
| **Mass Backdate Wizard** | Backdate multiple done transfers at once via a dedicated wizard. |
| **Domain Filter** | Use standard Odoo domain syntax to select which transfers to backdate. |
| **“Backdate Selected” Action** | From the Transfers list, select lines and run **Action → Backdate Selected Transfers**; the wizard opens with the selection pre-filled. |
| **Accounting Option** | Optional update of linked posted journal entry dates to the backdate (reconciled entries are skipped). |
| **Audit Trail** | Stores original completion date, user who backdated, and reason on the transfer. |
| **Security** | Access restricted to the **Inventory Backdate Manager** group. |

---

## Requirements

- **Odoo:** 18.0
- **Dependencies:** `stock`, `stock_account` (for accounting date update)

---

## Installation (Step by Step)

### 1. Place the module in the addons path

- Copy the `inventory_backdate_advanced` folder into one of your Odoo addons paths (e.g. `addons` or a custom `project` directory).
- Ensure the parent directory is in `addons_path` in your Odoo configuration (`odoo.conf` or command line).

**Example `odoo.conf`:**
```ini
[options]
addons_path = /path/to/odoo/addons,/path/to/odoo/project
```

### 2. Restart Odoo

Restart the Odoo server so it detects the new module.

### 3. Update the Apps list

1. Log in as an administrator.
2. Enable **Developer Mode** (Settings → Activate the developer mode).
3. Go to **Apps**.
4. Click **Update Apps List** (if available).
5. Remove the “Apps” filter and search for **Advanced Inventory Backdate** (or the module name).

### 4. Install the module

1. Open **Advanced Inventory Backdate**.
2. Click **Install**.

---

## Configuration (Step by Step)

### 1. Assign the security group

Only users in **Inventory Backdate Manager** can use the wizard and see backdate fields.

1. Go to **Settings → Users & Companies → Users** (or **Groups**).
2. Open the user (or group) that should be allowed to backdate.
3. Under **Other**, find **Inventory / Inventory** (or the Inventory category).
4. Enable **Inventory Backdate Manager** for the relevant user(s).

**Alternative (group only):**

1. **Settings → Technical → Security → Groups**.
2. Search for **Inventory Backdate Manager**.
3. Add the desired users to this group.

### 2. Optional: Inventory and Accounting

- The module extends **Inventory**; no extra app is required beyond **Inventory** (and **Invoicing** if you use **stock_account**).
- If you use **stock_account** and want to align journal entry dates when backdating, ensure **Inventory Valuation** is configured as needed for your company; the module only updates the **date** of existing posted moves linked to the backdated stock move.

---

## Usage

### Method 1: Mass Backdate from Configuration menu

1. Go to **Inventory → Configuration → Mass Backdate** (menu at the bottom of the Configuration section).
2. **New Date:** Set the date/time to apply to the selected transfers.
3. **Reason for Backdate:** Enter a reason (required; stored for audit).
4. **Recalculate Inventory Valuation:**  
   - If checked: posted journal entries linked to the backdated stock moves will have their **date** set to the backdate (reconciled lines are skipped).  
   - If unchecked: only stock transfer and move dates are updated.
5. **Transfers Filter Domain:**  
   - Use Odoo domain syntax to select transfers. Only transfers in state **Done** are processed.  
   - Examples:
     - `[('state', '=', 'done')]`  
     - `[('state', '=', 'done'), ('picking_type_code', '=', 'outgoing')]`  
     - `[('state', '=', 'done'), ('date_done', '>=', '2025-01-01')]`
6. Click **Apply Mass Backdate**.

### Method 2: Backdate selected transfers from the list

1. Go to **Inventory → Operations → Transfers** (or **All Operations**).
2. Filter or search for the transfers you want (e.g. state = Done).
3. Select one or more transfers (checkboxes).
4. Open the **Action** menu (top of the list).
5. Click **Backdate Selected Transfers**.
6. The wizard opens with the **Transfers Filter Domain** pre-filled with the selected transfer IDs (e.g. `[('id', 'in', [1, 2, 3])]`).
7. Set **New Date**, **Reason for Backdate**, and optionally **Recalculate Inventory Valuation**.
8. Click **Apply Mass Backdate**.

### Viewing the audit trail

On a backdated transfer:

1. Open the transfer form.
2. After **Effective Date** (`date_done`), the following fields are shown (for users with **Inventory Backdate Manager**):
   - **Original Date Done:** Completion date before backdate.
   - **Backdated By:** User who performed the backdate.
   - **Backdate Reason:** Reason entered in the wizard.

---

## Technical details

| Item | Detail |
|------|--------|
| **Extended models** | `stock.picking`, `stock.move` (Stock Move Line and Accounting Entry are updated by the wizard, not extended) |
| **New model** | `stock.backdate.wizard` (transient) |
| **Security group** | `inventory_backdate_advanced.group_inventory_backdate_manager` |
| **Access** | Only the wizard has explicit access rights; picking/move use existing stock rights. |
| **Domain** | Domain string is parsed with `ast.literal_eval` (no `eval`) for safety. |
| **Accounting** | When “Recalculate Inventory Valuation” is used, only **posted** `account.move` with `stock_move_id` are considered; moves with reconciled lines are not updated. |

---

## Domain examples (Transfers Filter Domain)

- All done transfers:  
  `[('state', '=', 'done')]`
- Done outgoing deliveries:  
  `[('state', '=', 'done'), ('picking_type_code', '=', 'outgoing')]`
- Done receipts:  
  `[('state', '=', 'done'), ('picking_type_code', '=', 'incoming')]`
- Done in a date range:  
  `[('state', '=', 'done'), ('date_done', '>=', '2025-01-01'), ('date_done', '<=', '2025-01-31')]`
- Specific IDs (e.g. from “Backdate Selected Transfers”):  
  `[('id', 'in', [1, 2, 3])]`

---

## Troubleshooting

| Issue | What to check |
|-------|----------------|
| Menu **Mass Backdate** not visible | User must have **Warehouse Management** (Stock Manager) or **Inventory Backdate Manager**. Upgrade the module if you just changed groups. |
| **Backdate Selected Transfers** not in Action menu | Same groups; ensure you are on a **Transfers** (stock.picking) list view. |
| “Invalid domain” | Domain must be valid Python list of tuples, e.g. `[('state', '=', 'done')]`. No trailing comma issues; strings in quotes. |
| “No stock transfers found” | Domain may not match any record; try a broader domain like `[('state', '=', 'done')]`. |
| “None of the selected transfers are in the 'Done' state” | Only **Done** transfers are processed; confirm selection and domain. |
| Journal entry date not changing | Only **posted** moves are updated; reconciled lines are skipped. Check **stock_account** is installed and journal is linked. |

---

## License

LGPL-3.
