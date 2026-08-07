# RMA Management — User Guide (Odoo 18)

End-to-end walkthrough of every feature in the `rma_management` module with concrete examples.

---

## Table of Contents
1. [Overview](#1-overview)
2. [Installation](#2-installation)
3. [Security & Access Groups](#3-security--access-groups)
4. [Configuration](#4-configuration)
5. [Customer RMA — Website Flow](#5-customer-rma--website-flow)
6. [Customer RMA — Backend Flow](#6-customer-rma--backend-flow)
7. [Supplier RMA — Backend Flow](#7-supplier-rma--backend-flow)
8. [Product-Level Configuration](#8-product-level-configuration)
9. [Mail Notifications](#9-mail-notifications)
10. [Reporting & Dashboards](#10-reporting--dashboards)
11. [Data Model Reference](#11-data-model-reference)
12. [FAQ](#12-faq)

---

## 1. Overview

The RMA (Return Merchandise Authorization) module provides complete return workflows for both customers and suppliers in Odoo 18. Fully integrated with **Sales**, **Purchase**, **Inventory**, and **Accounting**, it automates the entire return lifecycle — from request creation through stock movement to refund/replacement settlement.

### Core Capabilities
- **Customer RMA**: Portal-driven return requests linked to Sale Orders
- **Supplier RMA**: Vendor returns initiated from Purchase Orders
- **Auto-generated documents**: Return pickings, replacement sales orders, credit notes (customer & vendor)
- **Configurable reasons**: Each reason has a default action (Refund / Replacement / Return Only / No Action / Contact Support)
- **Restocking fees**: Percentage or fixed amount
- **Product threshold**: Skip physical pickup for low-value lines
- **Bulk reason apply**: One click applies a reason/action to every line
- **Full audit trail**: Chatter, mail templates, activity scheduling

---

## 2. Installation

### A. Via the UI
1. Copy the `rma_management` folder into your Odoo addons path (e.g. `/opt/odoo/custom/`).
2. Restart Odoo.
3. Go to **Apps → Update Apps List**.
4. Search for **"RMA Management"** → click **Activate**.

### B. Via CLI
```bash
./odoo-bin -c odoo.conf -d your_db -i rma_management --stop-after-init
```

### Dependencies (auto-installed)
- `sale_management`
- `purchase`
- `stock`
- `account`
- `website_sale`
- `portal`

---

## 3. Security & Access Groups

Two groups are created under **Settings → Users & Companies → Users**:

| Group | Permissions |
|-------|-------------|
| **RMA / User** | Create, read, update customer & supplier RMAs. Cannot edit config. |
| **RMA / Manager** | Full access including Reasons, Restock Fees, Product Types, Mail Templates. |

**Portal users** automatically get access to their own RMAs (via an `ir.rule`) — they can see only RMAs whose `partner_id` matches their contact.

### Example: Assign User
```
Settings → Users → (pick user) → Access Rights tab
→ RMA Management = "Manager"  (or "User")
→ Save
```

---

## 4. Configuration

### 4.1 RMA Reasons
**Menu**: `RMA Management → Configuration → Reasons`

Six reasons ship by default (matching the spec):

| Reason | Default Action |
|--------|----------------|
| Wrong quantity, size, or colour received | Replacement |
| Damaged or Defective item | Return & Refund |
| Do not need / ordered wrong color/size/quantity | Return & Refund |
| Item missing | Replacement |
| Received excess quantity | Only Return |
| Shipped to wrong address / Lost box / Other | Contact Support |

**Action types available**:
- `Return & Refund` — pickup + credit note
- `Replacement` — pickup + new sales/purchase order
- `Only Return` — pickup only, no financial impact
- `NO ACTION` — customer keeps item, no pickup
- `Contact Support` — routes outside standard flow

**Add a new reason — Example**:
```
Reason:        Packaging damaged in transit
Action:        Return & Refund
Service Charge: 10.00
Active:        Yes
```

### 4.2 Restocking Fees
**Menu**: `RMA Management → Configuration → Restock Fees`

Configurable percentage or fixed deduction from refunds.

**Example 1 — Percentage**:
```
Name:    Standard 15% Handling Fee
Type:    Percentage (%)
Amount:  15.0
Active:  ✓
```
If a refund total is ₹1000 and this fee is active → refund becomes ₹1000 − (15% × ₹1000) = **₹850**. The ₹150 appears on the credit note as a negative line labelled *"Restocking Fee"*.

**Example 2 — Fixed**:
```
Name:    Flat ₹50 Handling Fee
Type:    Fixed Amount
Amount:  50.0
```

> Only the first **active** restocking fee is applied. Keep only one active at a time.

### 4.3 RMA Product Types
**Menu**: `RMA Management → Configuration → Product Types`

Used to categorize products for reporting and return eligibility.

**Defaults**: `Electronics`, `Fragile`

**Example**:
```
Name:         Hazardous
Description:  Items that require special handling on return
Active:       ✓
```

### 4.4 Mail Templates
**Menu**: `RMA Management → Configuration → Mail Templates` (Manager only)

Four templates are preloaded — edit subject, body, recipients freely:
| Template | Trigger |
|----------|---------|
| RMA Submitted Notification | `action_submit()` |
| RMA Approved Notification | `action_approve()` |
| RMA Closed Notification | `action_close()` |
| RMA Rejected Notification | reject wizard confirm |

**Example customization**:
```
Subject:   [{{ object.company_id.name }}] RMA {{ object.name }} approved
Body:      Dear {{ object.partner_id.name }}, ...
```

---

## 5. Customer RMA — Website Flow

### 5.1 Customer submits a return

**Prerequisites**: Customer has a confirmed Sale Order with delivered quantity.

**Steps**:
1. Customer logs in → `/my` (My Account).
2. Click **"Orders"** → opens order list.
3. Open an order → the page shows a blue **"Return Products"** button (visible when `sale_order.state == 'sale'`).
4. Click it → lands on `/my/rma/create/<order_id>`.
5. Fills the form:
   - **Return Address** — dropdown of customer's addresses (default: order's shipping address)
   - **Apply Reason / Action to All** — two dropdowns + *"Apply to All"* button (optional, JS-powered)
   - Per line:
     - ✅ Checkbox to include the line
     - Return quantity (max = delivered qty)
     - Reason dropdown
     - Action: Refund / Replacement / Return Only

**Example — 3-product order**:
| Product | Delivered | Return | Reason | Action |
|---------|-----------|--------|--------|--------|
| Office Chair | 2 | ✅ 1 | Damaged | Refund |
| Desk Lamp | 4 | ✅ 4 | Wrong colour | Replacement |
| Keyboard | 1 | ☐ (skip) | — | — |

Unchecked lines are skipped server-side.

6. Click **"Submit Return Request"** → redirects to `/my/rma/<id>` detail page with status badge.

### 5.2 Customer tracks a return

**Menu**: `My Account → Returns` (top-level `/my/returns`)

Shows list of all RMAs for the customer:
| RMA # | Order | Date | Items | Status |
|-------|-------|------|-------|--------|
| CRMA-00007 | S00012 | 20/04/2026 | 2 | Submitted |

Click any RMA → detail page with:
- Products, qty, reason, action
- **Pickup Required** badge per line (shows threshold effect)
- Total refund amount (currency-aware)
- Rejection reason if rejected

---

## 6. Customer RMA — Backend Flow

### 6.1 State machine

```
 Draft ──Submit──> Submitted ──Approve──> Approved ──Start Processing──> Processing ──Close──> Closed
                       │                                                                        
                       └──Reject (wizard)──> Rejected ──Reset to Draft──> Draft
```

### 6.2 Example: full backend workflow

**Menu**: `RMA Management → Customer RMA → Returns → New`

#### Step 1 — Fill header
```
Sale Order:     S00015
Customer:       Azure Interior        (auto-filled)
Return Address: <auto-filled>
Date:           2026-04-24
Priority:       Normal
```

#### Step 2 — Add RMA lines

Click **"Add a line"** in the RMA Lines tab:
| Product | Delivered | Return Qty | Reason | Action | Unit Price | Total |
|---------|-----------|------------|--------|--------|------------|-------|
| Office Chair | 2.0 | 1.0 | Damaged | Return & Refund | 120.00 | 120.00 |
| Desk Lamp | 4.0 | 2.0 | Wrong colour | Replacement | 45.00 | 90.00 |

> Only products from the selected Sale Order appear in the dropdown (domain filtered via `valid_product_ids`).

#### Step 3 — (Optional) Bulk apply reason

If all lines share the same reason, use the **"Bulk Apply Reason"** group:
```
Apply Reason to All Lines: Damaged
[Apply to All Lines] → sets reason + default action on every line
```

#### Step 4 — Submit
Click **Submit** button in header → state becomes `Submitted` → email goes out to customer.

#### Step 5 — Approve
Click **Approve** → three documents can auto-generate based on line actions:

| Line action | Document created |
|-------------|------------------|
| Return & Refund | Return Picking + Credit Note (Draft `out_refund`) |
| Replacement | Return Picking + Replacement Sale Order |
| Only Return / No Action | Return Picking only |

Three **smart buttons** appear on the form:
- 📦 **Return Picking** (`WH/IN/xxxxx`)
- ✏️ **Credit Note** (`account.move` draft `out_refund`)
- 💵 **Replacement** (`sale.order`)

#### Step 6 — Process and Close
- Click **Start Processing** → state becomes `Processing` (warehouse team picks up, validates incoming shipment).
- Once items returned & credit/replacement settled → click **Close** → state becomes `Closed` → email notification sent.

#### Step 7 — Rejection path (alt)
From `Submitted`, click **Reject** → wizard pops up:
```
Reason for Rejection: Return window (30 days) expired on 2026-04-01.
[Reject Claim] → state = Rejected, email goes out with the reason
```

If wrong rejection: click **Reset to Draft** → back to Draft.

### 6.3 Threshold-aware pickup

If a product has `rma_threshold` set and the requested **return qty < threshold**, that line is **skipped** from the Return Picking (pickup cost would exceed product value).

**Example**:
```
Product "Cheap Cable" (list_price 50, rma_threshold 3)
Customer returns qty = 2 → no pickup line created for this row
But the credit note / replacement still generates normally.
```

On the RMA list and portal detail, the line shows:
- Pickup column → "Not Required" (green badge) or "Required" (blue badge)

---

## 7. Supplier RMA — Backend Flow

### 7.1 Example: create from Purchase Order

**Menu**: `Purchases → Orders → <any confirmed PO>`

1. Click the **"RMAs"** smart button on the PO form → opens filtered list.
2. Click **New** (or use `RMA Management → Supplier RMA → Returns → New`).
3. Pick the Purchase Order → lines auto-populate from PO `qty_received`.

#### Header
```
Purchase Order:  P00021
Vendor:          Acme Suppliers (auto-filled)
Receipt Email:   orders@acme.com
Receipt Phone:   +91-98-xxx
Date:            2026-04-24
Deadline:        2026-05-01
```

#### Lines (auto-populated from PO)
| Product | Delivered | Return Qty | Reason | Action | Unit Price | Total |
|---------|-----------|------------|--------|--------|------------|-------|
| Keyboard | 100 | 5 | Damaged | Return & Refund | 800 | 4000 |
| Mouse | 50 | 0 | — | — | 200 | 0 |

Edit Return Qty to zero-out lines you don't want to return.

### 7.2 Bulk Apply Reason
```
Apply Reason to All Lines: Damaged
[Apply to All Lines] → writes reason + default action on all lines
```

### 7.3 Submit → Approve

- **Submit** → state `Submitted`
- **Approve** → auto-creates:
  - **Outgoing Picking** (stock → vendor location) for every line with `return_qty > 0`
  - **Incoming Picking** (vendor → stock) for each entry in Replacement Product Lines tab
  - **Vendor Credit Note** (`in_refund`) for lines with action `return_refund`

### 7.4 Example output

After approve on SRMA-00004:
```
Outgoing Picking:  WH/OUT/00021  (5× Keyboard → Acme)
Incoming Picking:  WH/IN/00034   (for replacement products)
Vendor Credit Note: BILL/2026/0005 (draft)
```

Smart buttons on the form take you directly to each document.

### 7.5 Process → Close
Same as customer side: **Start Processing → Close** once everything settles.

---

## 8. Product-Level Configuration

**Menu**: `Inventory → Products → <product> → Inventory tab → RMA Configuration`

Three fields inherited onto `product.template`:

| Field | Purpose | Example |
|-------|---------|---------|
| RMA Product Type | Classification for reports | "Electronics" |
| RMA Return Qty Threshold | Skip pickup below this qty | `3.0` |
| Default RMA Reason | Pre-selected reason when added to RMA | "Damaged or Defective item" |

**Example**:
```
Product:              Low-Cost Charger
RMA Product Type:     Electronics
Threshold:            5.0
Default Reason:       Damaged or Defective item
```

Result: When a customer adds this product to an RMA line, the reason auto-fills; if return qty < 5, no pickup is scheduled.

---

## 9. Mail Notifications

Three customer-facing emails + one closure email fire automatically:

| Event | Template | Recipient |
|-------|----------|-----------|
| `action_submit` | `email_template_rma_submitted` | Customer |
| `action_approve` | `email_template_rma_approved` | Customer |
| `action_close` | `email_template_rma_closed` | Customer |
| Reject wizard | `email_template_rma_rejected` | Customer (includes rejection reason) |

All chatter messages, state transitions, and field changes are logged on the RMA record via `mail.thread`. Users can add internal notes or log activities.

---

## 10. Reporting & Dashboards

### 10.1 Kanban
**Menu**: `RMA Management → Customer RMA → Returns` → click **Kanban** icon

Groups by state (Draft / Submitted / Approved / Processing / Closed / Rejected). Each card shows RMA #, customer, order, date, and total refund.

### 10.2 Graph + Pivot (Dashboard)
**Menu**: `RMA Management → Dashboard`

- Bar chart: refund amount grouped by state
- Pivot: date (month) × state, measure = refund

### 10.3 List with decorations
Customer list uses color coding:
- Blue = Submitted
- Green = Approved / Closed
- Red = Rejected
- Grey = Draft

### 10.4 Search filters
Both RMA lists support:
- State filters (Draft, Submitted, Approved, Processing, Closed, Rejected)
- "My RMAs" (responsible = current user)
- Group by: Customer / Vendor, Status, Date

### 10.5 Printable PDF
From any Customer RMA form → ⚙️ **Print → RMA Report** generates a QWeb-PDF with returned products, replacement lines, and notes.

---

## 11. Data Model Reference

| Model | Purpose |
|-------|---------|
| `customer.rma` | Customer RMA header |
| `customer.rma.line` | Customer RMA line (one per returned product) |
| `customer.rma.replacement.line` | Extra products sent as replacement |
| `supplier.rma` | Supplier RMA header |
| `supplier.rma.line` | Supplier RMA line |
| `supplier.rma.replacement.line` | Vendor replacement lines |
| `rma.reason` | Configurable reasons with default action |
| `rma.restock.fee` | Percentage/fixed restock fee config |
| `rma.product.type` | Product-type classification |
| `rma.reject.wizard` | TransientModel for reject flow |
| `sale.order` (ext.) | `rma_count`, `action_view_rma` |
| `purchase.order` (ext.) | `rma_count`, `action_view_rma` |
| `product.template` (ext.) | `rma_product_type_id`, `rma_threshold`, `rma_reason_id` |

Key sequences:
- `customer.rma` → `CRMA-00001`, `CRMA-00002`, …
- `supplier.rma` → `SRMA-00001`, `SRMA-00002`, …

---

## 12. FAQ

**Q. Can a customer submit multiple products in one return?**
A. Yes. The portal form lists every delivered line of the order; tick what you want to return.

**Q. Can the same reason be applied to all products?**
A. Yes — use the *"Apply to All"* button on the portal form or the **Bulk Apply Reason** group on the backend form.

**Q. Are refunds and replacements both supported?**
A. Yes, both — selectable per line. Mixing refund and replacement on the same RMA works; the system creates a credit note for refund lines and a replacement Sale Order for replacement lines.

**Q. Do customers get email notifications?**
A. Yes — for submit, approve, reject, and close. Templates are fully editable from the RMA Configuration menu.

**Q. How does the threshold quantity work?**
A. Set `rma_threshold` on a product. If a customer requests a return quantity **below** that threshold, the line is excluded from the Return Picking (no pickup), but a credit note or replacement still runs normally. Useful when pickup cost > product value.

**Q. How is restocking fee applied?**
A. Configure one active `rma.restock.fee` — percentage or fixed. On approve, it's added as a negative line on the credit note with the label *"Restocking Fee"*. Only the first active config applies.

**Q. Can I reject a submitted RMA?**
A. Yes — the Reject button on `Submitted` state opens a wizard where you enter a reason. Customer gets an email with the reason. The RMA can later be reset to Draft.

**Q. Does it integrate with Inventory?**
A. Yes — every approve creates real `stock.picking` records (incoming for customer, outgoing for supplier). Warehouse team processes them in the standard Inventory module.

**Q. Does it integrate with Accounting?**
A. Yes — credit notes are real `account.move` records in draft. Accountants post them in their usual flow.

**Q. Can portal users see only their own RMAs?**
A. Yes — an `ir.rule` on `base.group_portal` restricts by `partner_id = user.partner_id`.
