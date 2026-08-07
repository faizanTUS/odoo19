# RMA Management — Testing Guide (Odoo 18)

Step-by-step test scenarios to verify every feature works. Includes manual UI tests, shell-based integration checks, and sample data setups you can copy-paste.

---

## Table of Contents
1. [Setup a Fresh Test Environment](#1-setup-a-fresh-test-environment)
2. [Install & Verify Module Load](#2-install--verify-module-load)
3. [Configuration Tests](#3-configuration-tests)
4. [Customer RMA — Backend Tests](#4-customer-rma--backend-tests)
5. [Customer RMA — Portal Tests](#5-customer-rma--portal-tests)
6. [Supplier RMA — Backend Tests](#6-supplier-rma--backend-tests)
7. [Product Threshold Tests](#7-product-threshold-tests)
8. [Bulk Reason Apply Tests](#8-bulk-reason-apply-tests)
9. [Security & Access Tests](#9-security--access-tests)
10. [Mail Notification Tests](#10-mail-notification-tests)
11. [Reject & Reset Tests](#11-reject--reset-tests)
12. [Smart Buttons & Counts](#12-smart-buttons--counts)
13. [Automated Shell Smoke Test](#13-automated-shell-smoke-test)
14. [Troubleshooting](#14-troubleshooting)

---

## 1. Setup a Fresh Test Environment

### 1.1 Dedicated config
Create `/path/to/conf/rma_test.conf`:
```ini
[options]
admin_passwd = admin
db_host = localhost
db_port = 5432
db_name = rma_test_db
xmlrpc_port = 8070
db_user = odoo
db_password = odoo
addons_path = /path/to/odoo/addons,/path/to/custom/rma
```

### 1.2 Fresh database
```bash
PGPASSWORD=odoo psql -h localhost -U odoo -d postgres \
  -c "DROP DATABASE IF EXISTS rma_test_db;"
PGPASSWORD=odoo psql -h localhost -U odoo -d postgres \
  -c "CREATE DATABASE rma_test_db OWNER odoo;"
```

---

## 2. Install & Verify Module Load

### Test 2.1 — Clean install
```bash
./odoo-bin -c /path/to/conf/rma_test.conf -d rma_test_db \
    -i base,rma_management --stop-after-init --without-demo=all
```

**Expected log**:
```
Loading module rma_management (...)
module rma_management: creating or updating database tables
loading rma_management/security/rma_security.xml
loading rma_management/security/ir.model.access.csv
loading rma_management/data/rma_data.xml
...
Module rma_management loaded in X.Xs, NNN queries
```

**Pass criteria**: exit code `0`, no `ERROR` / `CRITICAL` / `Traceback` in log.

### Test 2.2 — Upgrade
```bash
./odoo-bin -c /path/to/conf/rma_test.conf -d rma_test_db \
    -u rma_management --stop-after-init
```
Same pass criteria.

### Test 2.3 — Server runs
```bash
./odoo-bin -c /path/to/conf/rma_test.conf
```
Open `http://localhost:8070`, log in as `admin`/`admin`, main menu shows **"RMA Management"**.

---

## 3. Configuration Tests

### Test 3.1 — Default data loaded
**Menu**: `RMA Management → Configuration → Reasons`

**Expected**: 6 reasons preloaded.
| Name | Action |
|------|--------|
| Wrong quantity, size, or colour received | Replacement |
| Damaged or Defective item | Return & Refund |
| Do not need / ordered wrong color, size, or quantity | Return & Refund |
| Item missing | Replacement |
| Received excess quantity | Only Return |
| Shipped to the wrong address / Lost box / Other | Contact Support |

### Test 3.2 — Create a new reason
```
Name:            Packaging damaged
Action:          Return & Refund
Service Charge:  20.00
Active:          ✓
```
Click **Save**. Record appears in list.

### Test 3.3 — Product Types
**Menu**: `RMA Management → Configuration → Product Types`
**Expected**: `Electronics`, `Fragile` preloaded.

### Test 3.4 — Restocking Fee
**Menu**: `RMA Management → Configuration → Restock Fees`
**Default shipped**: `Standard 15% Handling Fee` (inactive).

Toggle Active → `✓`. It will now auto-apply to future credit notes.

### Test 3.5 — Mail Templates
**Menu**: `RMA Management → Configuration → Mail Templates`
**Expected**: 4 templates filtered to `customer.rma`:
- RMA Submitted Notification
- RMA Approved Notification
- RMA Closed Notification
- RMA Rejected Notification

Open any → confirm subject + body render. Edit freely.

---

## 4. Customer RMA — Backend Tests

### Test 4.1 — Create Customer RMA
**Pre-req**: have a confirmed Sale Order with delivered qty.

1. **Menu**: `RMA Management → Customer RMA → Returns → New`
2. Pick `Sale Order = S00001`.
3. **Expected**: `Customer`, `Return Address` auto-fill.
4. Add a line:
   | Product | Return Qty | Reason | Action |
   |---------|-----------|--------|--------|
   | Conference Chair | 1 | Damaged | Return & Refund |
5. Save.

**Pass**: RMA gets name `CRMA-00001`, state `Draft`.

### Test 4.2 — Submit
Click **Submit** button in header.
**Pass**: state → `Submitted`, chatter shows state change, email sent (check Outgoing Emails under Settings → Technical).

### Test 4.3 — Approve
Click **Approve**.
**Pass**:
- state → `Approved`
- Three smart buttons appear: Return Picking, Credit Note, Replacement (depending on line actions)
- Return Picking exists in **Inventory → Operations → Transfers**
- Credit Note exists as `draft out_refund` in **Accounting → Customers → Credit Notes**
- Customer receives approval email

### Test 4.4 — Start Processing → Close
Click **Start Processing** → state = `Processing`.
Click **Close** → state = `Closed`, closed email sent.

### Test 4.5 — Multi-action line mix
Create an RMA with two lines:
| Line 1 | Return & Refund |
| Line 2 | Replacement |

On Approve:
- Credit Note has **only Line 1** product.
- Replacement SO has **only Line 2** product.
- Return Picking has **both** products (unless thresholds skip them).

### Test 4.6 — Priority field
Set priority = `High` ⭐⭐ → saved, displays correctly.

### Test 4.7 — Currency
Fill currency via the linked sale order. `Total Refund Amount` and `Restocking Fee` display in the SO's currency.

---

## 5. Customer RMA — Portal Tests

### Test 5.1 — Portal user sees "Return Products" button
1. Create a portal user (grant portal access to any `res.partner` → Action → Grant Portal Access).
2. Log in as that portal user.
3. Navigate `/my/orders/<id>` of a confirmed order.

**Pass**: Blue "Return Products" button visible.

### Test 5.2 — Submit return from portal
1. Click **Return Products**.
2. Form appears with:
   - Return Address dropdown (customer + child contacts)
   - Apply Reason/Action to All dropdowns + button
   - Per-line checkbox, qty, reason, action columns
3. Tick two lines, enter qty, pick reasons, click **Apply to All** with a reason + action "Refund".
   **Pass**: every ticked line's reason + action dropdown updates.
4. Untick one line.
5. Click **Submit Return Request**.

**Pass**:
- Redirects to `/my/rma/<id>`
- RMA created in state `Submitted`
- Only ticked lines present
- In backend, the new record appears under `RMA Management → Customer RMA → Returns`

### Test 5.3 — Portal list
Navigate `/my/returns`.
**Pass**: table shows RMA #, order, date, item count, status badge.

### Test 5.4 — Portal detail
Click any RMA row.
**Pass**: page shows products, qty, reason, action, Pickup Required badge, refund total.

### Test 5.5 — Cross-partner isolation
Portal user of Partner A should NOT see Partner B's RMAs.
- Create RMA on Partner B (via backend).
- Log in as Partner A portal user → `/my/returns` → B's RMA must NOT appear.
- Navigate directly to B's RMA URL `/my/rma/<b_id>` → redirects to `/my`.

**Pass**: `ir.rule` enforces partner scoping.

---

## 6. Supplier RMA — Backend Tests

### Test 6.1 — Create from Purchase Order smart button
1. Open any confirmed PO with received qty.
2. Click **"RMAs"** smart button.
3. Click **New**.

### Test 6.2 — Select PO auto-populates lines
1. **Menu**: `RMA Management → Supplier RMA → Returns → New`
2. Pick `Purchase Order = P00001`.
3. **Pass**: Lines auto-populate from PO's order_lines with `delivered_qty = qty_received`, return_qty = 0, unit_price filled.

### Test 6.3 — Edit return qty and submit
1. Change return_qty on one line to `2`.
2. Click **Submit** → state `Submitted`.
3. Click **Approve**.

**Pass**:
- Outgoing Picking created (WH/OUT/xxxxx) — only the `return_qty > 0` line
- Vendor Credit Note created (`in_refund` draft) for `return_refund` lines
- If replacement lines tab has entries → Incoming Picking also created

### Test 6.4 — Replacement product line
1. Add a row under **Replacement Product Line** tab:
   | Product | Qty | Price |
   |---------|-----|-------|
   | Keyboard | 2 | 0 |
2. Approve.

**Pass**: Incoming Picking scheduled to receive 2× Keyboard from vendor location.

### Test 6.5 — Smart buttons
After approve → three smart buttons show:
- 📦 **Outgoing** (WH/OUT/xxxxx)
- 📦 **Incoming** (WH/IN/xxxxx) — only if replacement lines
- ✏️ **Credit Note** (`in_refund`)

Click each → opens the target record.

---

## 7. Product Threshold Tests

### Test 7.1 — Configure threshold on product
1. **Inventory → Products → Conference Chair**
2. Inventory tab → RMA Configuration
3. Set `RMA Return Qty Threshold = 3.0`
4. Save.

### Test 7.2 — Verify line with qty < threshold skips picking
1. Create Customer RMA with this product, `Return Qty = 2`.
2. Approve.
3. **Expected**:
   - `line.pickup_required = False` (view under "Pickup" column)
   - Return Picking does **NOT** contain this product's move
   - Credit Note **does** contain the refund line (threshold only skips physical pickup)

### Test 7.3 — Verify line with qty >= threshold triggers picking
Same product, same setup, but `Return Qty = 3`.
- `line.pickup_required = True`
- Return Picking contains the product

### Test 7.4 — Mixed threshold behavior
One RMA with two lines:
- Line A: product with threshold 3, qty 2 → skip pickup
- Line B: product with threshold 3, qty 5 → pickup required

**Pass**: Return Picking has **only** Line B product. Credit note has both.

---

## 8. Bulk Reason Apply Tests

### Test 8.1 — Customer backend bulk
1. Create RMA with 3 lines, no reason set.
2. In the **"Bulk Apply Reason"** group, pick `Damaged or Defective item`.
3. Click **"Apply to All Lines"**.

**Pass**: All 3 lines get `reason_id = Damaged`, `action = Return & Refund`.

### Test 8.2 — Supplier backend bulk
Same as 8.1 but on `supplier.rma`. Also check action maps:
- Replacement reason → action `replacement`
- Return & Refund reason → action `return_refund`
- Only Return / No Action / Contact Support → action `return_refund` (supplier side)

### Test 8.3 — Portal bulk via JS
1. Portal return form with 3 ticked lines.
2. Select reason in "Apply Reason to All".
3. Select "Refund" in "Apply Action to All".
4. Click **Apply to All**.

**Pass**: All ticked lines' reason + action dropdowns update (via inline JS).

### Test 8.4 — Portal bulk respects checkbox
Untick one line, then click Apply to All.
**Pass**: Unticked line is NOT updated.

---

## 9. Security & Access Tests

### Test 9.1 — RMA User cannot edit config
1. Assign user the group `RMA / User` only.
2. Log in → `RMA Management` menu visible but `Configuration` submenu hidden.

**Pass**: Configuration submenu has `groups="rma_management.group_rma_manager"`.

### Test 9.2 — RMA Manager can edit everything
1. Assign `RMA / Manager`.
2. Configuration menu visible → can create/edit/delete reasons, fees, types, templates.

### Test 9.3 — Portal access to own RMAs only
Covered in Test 5.5.

### Test 9.4 — Portal cannot create via backend
1. Log in as portal user.
2. Try to access backend `/web#action=rma_management.action_customer_rma` directly.

**Pass**: `403` or redirect — portal users have no backend access.

### Test 9.5 — ACL covers all 10 models
Verify via:
```bash
cd custom/rma/rma_management
python3 -c "
import re, csv, glob
models = set()
for f in glob.glob('models/*.py'):
    for m in re.finditer(r'_name\s*=\s*[\"\'']([\w.]+)[\"\'']', open(f).read()):
        models.add(m.group(1))
acls = set()
with open('security/ir.model.access.csv') as f:
    for row in csv.DictReader(f):
        acls.add(row['model_id:id'][6:].replace('_','.'))
for m in models:
    assert 'model_' + m.replace('.','_') in open('security/ir.model.access.csv').read(), f'No ACL for {m}'
print('All models have ACL rows')
"
```

---

## 10. Mail Notification Tests

### Test 10.1 — Email settings
Settings → General Settings → Discuss → configure Outgoing Mail Server (can use an SMTP test server like MailHog for local testing).

### Test 10.2 — Submit email
Submit a Customer RMA → check **Settings → Technical → Email → Emails** for a pending email.
**Pass**: To = customer email, Subject contains RMA name.

### Test 10.3 — Approve email
Approve → another email queued.

### Test 10.4 — Reject email includes reason
Reject with wizard reason "Out of window" → email body contains "Out of window".

### Test 10.5 — Close email
Close → fourth email queued.

---

## 11. Reject & Reset Tests

### Test 11.1 — Reject wizard
1. RMA in `Submitted` → click **Reject**.
2. Wizard opens, enter reason "30-day window expired".
3. Click **Reject Claim**.

**Pass**:
- state = `Rejected`
- `reject_reason` field populated
- Email sent
- "Other Info" tab shows rejection reason (visible only when state = Rejected)

### Test 11.2 — Reset to Draft from Rejected
On rejected RMA → click **Reset to Draft**.
**Pass**: state = `Draft`, editable again. `reject_reason` remains for audit.

### Test 11.3 — Supplier reject
Same flow on supplier RMA. Reject wizard must update `supplier.rma` not `customer.rma`.

---

## 12. Smart Buttons & Counts

### Test 12.1 — SO smart button count
1. Open Sale Order S00001.
2. Create 2 customer RMAs for it.
3. Refresh SO form.

**Pass**: "RMAs" smart button shows **2**. Click it → list filtered to these two.

### Test 12.2 — PO smart button count
Same logic on `purchase.order`.

### Test 12.3 — RMA form smart buttons
After approve, Return Picking / Credit Note / Replacement smart buttons appear only when those docs exist (controlled by `*_count` fields).

---

## 13. Automated Shell Smoke Test

Save this file as `/tmp/rma_smoke.py`:

```python
env = self.env  # noqa
print("=== RMA SMOKE TEST ===")

# 1. Data integrity
assert len(env['rma.reason'].search([])) >= 6
assert len(env['rma.product.type'].search([])) >= 2
assert len(env['mail.template'].search([('model', '=', 'customer.rma')])) >= 3

# 2. Security
assert env.ref('rma_management.group_rma_user')
assert env.ref('rma_management.group_rma_manager')
assert env.ref('rma_management.rule_customer_rma_portal_own')

# 3. Create customer, product, SO
partner = env['res.partner'].create({'name': 'SmokeCust'})
prod = env['product.product'].create({
    'name': 'SmokeProd', 'list_price': 100.0, 'type': 'consu',
    'rma_threshold': 2.0,
})
so = env['sale.order'].create({
    'partner_id': partner.id,
    'order_line': [(0, 0, {
        'product_id': prod.id, 'product_uom_qty': 5.0, 'price_unit': 100.0,
    })],
})
so.action_confirm()
for l in so.order_line:
    l.qty_delivered = 5.0

# 4. Customer RMA end-to-end
rma = env['customer.rma'].create({
    'sale_order_id': so.id, 'partner_id': partner.id,
    'rma_line_ids': [(0, 0, {
        'product_id': prod.id, 'quantity': 3.0, 'delivered_qty': 5.0,
        'unit_price': 100.0, 'action': 'return_refund',
        'reason_id': env.ref('rma_management.reason_damaged').id,
    })],
})
rma.action_submit()
assert rma.state == 'submitted'
rma.action_approve()
assert rma.state == 'approved'
assert rma.picking_id, "picking missing"
assert rma.credit_note_id, "credit note missing"
assert rma.total_refund_amount == 300.0
rma.action_process()
rma.action_close()
assert rma.state == 'closed'

# 5. Threshold check
# Qty 3 > threshold 2 → pickup required
assert rma.rma_line_ids[0].pickup_required is True

# 6. Supplier RMA
vendor = env['res.partner'].create({'name': 'SmokeVendor', 'supplier_rank': 1})
po = env['purchase.order'].create({
    'partner_id': vendor.id,
    'order_line': [(0, 0, {
        'product_id': prod.id, 'product_qty': 10.0, 'price_unit': 80.0,
        'name': prod.name, 'date_planned': '2026-04-24',
    })],
})
po.button_confirm()
for l in po.order_line:
    l.qty_received = 10.0
srma = env['supplier.rma'].create({
    'purchase_order_id': po.id, 'partner_id': vendor.id,
    'rma_line_ids': [(0, 0, {
        'product_id': prod.id, 'return_qty': 2.0, 'unit_price': 80.0,
        'action': 'return_refund',
    })],
})
srma.bulk_reason_id = env.ref('rma_management.reason_damaged')
srma.action_apply_bulk_reason()
assert srma.rma_line_ids[0].reason_id
srma.action_submit()
srma.action_approve()
assert srma.outgoing_picking_id
assert srma.credit_note_id

# 7. Reject flow
rma2 = env['customer.rma'].create({
    'sale_order_id': so.id, 'partner_id': partner.id,
    'rma_line_ids': [(0, 0, {
        'product_id': prod.id, 'quantity': 1.0, 'delivered_qty': 5.0,
        'unit_price': 100.0, 'action': 'return_refund',
    })],
})
rma2.action_submit()
wiz = env['rma.reject.wizard'].create({
    'rma_id': rma2.id, 'model_name': 'customer.rma',
    'reject_reason': 'Window expired',
})
wiz.action_reject_confirm()
assert rma2.state == 'rejected'
assert rma2.reject_reason == 'Window expired'

env.cr.rollback()
print("=== ALL SMOKE TESTS PASSED ===")
```

### Run it
```bash
./odoo-bin shell -c /path/to/conf/rma_test.conf -d rma_test_db --no-http \
    < /tmp/rma_smoke.py
```

**Expected output tail**:
```
=== RMA SMOKE TEST ===
=== ALL SMOKE TESTS PASSED ===
```

Any `AssertionError` = a bug — see [Troubleshooting](#14-troubleshooting).

---

## 14. Troubleshooting

### ❌ `ImportError: cannot import name ...` during install
- Make sure the module path is in `addons_path` in your conf.
- Python version must be ≥ 3.10 for Odoo 18.

### ❌ `ParseError: while parsing ... <list editable="bottom">`
- You're on Odoo ≤ 16 — this module uses Odoo 17/18's `<list>` tag, not `<tree>`. Use Odoo 18.

### ❌ "Return Products" button not showing on portal
- Verify Sale Order is in state `sale` (confirmed).
- Verify user is logged in as the customer of that order.
- Clear browser cache (assets).

### ❌ Credit note not created on Approve
- No `account.journal` of type `sale` in the company. Install Accounting module fully and configure a COA.
- Check: `Accounting → Configuration → Journals` has at least one Sales journal.

### ❌ Portal user gets AccessError browsing `/my/rma/<id>`
- Verify ACL: row `access_customer_rma_portal` present in `ir.model.access.csv`.
- Verify ir.rule `rule_customer_rma_portal_own` exists.
- Recompute: `./odoo-bin -u rma_management -d rma_test_db --stop-after-init`.

### ❌ Bulk reason button does nothing on portal
- Check browser console — JS in template may have been stripped by a strict CSP. Whitelist inline scripts or move the handler into `portal_rma.js`.

### ❌ Sequence produces duplicate names
- Sequences are declared with `noupdate="1"` — after install they won't reset. If you want to reset, delete the `ir.sequence` records for codes `customer.rma` and `supplier.rma` in SQL.

### ❌ View not updating after edit
Re-run with `-u rma_management` or `-u rma_management --dev=xml` and refresh browser.

### Useful queries
```sql
-- Count RMAs by state
SELECT state, count(*) FROM customer_rma GROUP BY state;

-- Find all pending credit notes tied to RMAs
SELECT r.name, m.name, m.state
FROM customer_rma r
JOIN account_move m ON m.id = r.credit_note_id
WHERE m.state = 'draft';

-- Orphan RMA lines (should return 0 rows)
SELECT l.id FROM customer_rma_line l
LEFT JOIN customer_rma r ON l.rma_id = r.id
WHERE r.id IS NULL;
```

### Dev-mode URLs
- Models list: `/web#action=base.action_model_model`
- Views list: `/web#action=base.action_ui_view`
- Menu debug: `/web#action=base.action_ui_view_custom`
- Email queue: `/web#action=mail.action_view_mail_mail`

---

## Testing Checklist (tick off when done)

- [ ] Fresh install completes cleanly (exit 0, no errors in log)
- [ ] 6 default reasons + 2 product types + 4 mail templates loaded
- [ ] Customer RMA: draft → submitted → approved → processing → closed
- [ ] Supplier RMA: draft → submitted → approved (+ outgoing/incoming/credit note)
- [ ] Reject wizard works for both customer and supplier RMAs
- [ ] Portal "Return Products" button visible + form functional
- [ ] Portal "Apply to All" JS works
- [ ] Portal user sees only own RMAs
- [ ] Product threshold skips pickup correctly
- [ ] Bulk reason applies to all lines on backend
- [ ] Smart buttons on Sale/Purchase Order show count
- [ ] Email templates fire on submit/approve/reject/close
- [ ] Kanban view groups by state
- [ ] RMA Report PDF prints
- [ ] Automated shell smoke test passes
