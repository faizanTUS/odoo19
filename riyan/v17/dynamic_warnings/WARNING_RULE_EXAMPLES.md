# Dynamic Warnings – More Example Rules

Use these as templates when creating rules in **Settings → Dynamic Warnings → Warning Rules**.  
Copy **Name**, **Target Model**, **Message**, **Conditions**, and **Alert Style** into a new rule.

---

## Product Variant (`product.product`)

Use **Target Model: Product Variant** when the warning should appear on the product variant form (e.g. when opening a specific size/color).

| Name | Message | Conditions | Alert Style |
|------|---------|------------|-------------|
| Low stock | Only **{qty_available}** units on hand. Consider reordering. | `[('qty_available', '<', 10), ('qty_available', '>=', 0)]` | Warning |
| Out of stock | This variant is out of stock (0 on hand). | `[('qty_available', '<=', 0)]` | Danger |
| Negative stock | Negative stock: **{qty_available}** units. Check inventory. | `[('qty_available', '<', 0)]` | Danger |
| Storable with no stock | Storable product with no stock. | `[('type', '=', 'product'), ('qty_available', '<=', 0)]` | Warning |
| Not sellable | This variant is not sellable (Sales checkbox unchecked). | `[('sale_ok', '=', False)]` | Info |
| Not purchasable | This variant is not purchasable (Purchase checkbox unchecked). | `[('purchase_ok', '=', False)]` | Info |

---

## Product Template (`product.template`)

Use **Target Model: Product** (Product Template) when the warning should appear on the main product form (one product, all variants).

| Name | Message | Conditions | Alert Style |
|------|---------|------------|-------------|
| No image | This product has no image. | `[('image_128', '=', False)]` | Info |
| Low stock (any variant) | Some variants may be low on stock. Check the variants. | `[('qty_available', '<', 10)]` | Warning |
| Not sellable | This product is not sellable. | `[('sale_ok', '=', False)]` | Info |

*Note: On product template, `qty_available` may aggregate or show a default variant value depending on your Odoo version.*

---

## Contact / Partner (`res.partner`)

| Name | Message | Conditions | Alert Style |
|------|---------|------------|-------------|
| Missing email | Email is missing. Please complete contact details. | `[('email', '=', False)]` | Warning |
| Missing phone | Phone number is missing. | `[('phone', '=', False)]` | Info |
| Missing email or phone | Contact has no email or phone. | `['|', ('phone', '=', False), ('email', '=', False)]` | Warning |
| Overdue receivables | This customer has overdue receivables. | `[('total_due', '>', 0)]` *or* use your custom overdue field | Danger |
| No address | Street address is not set. | `[('street', '=', False)]` | Info |
| Company contact without company | This is a contact but linked company is missing. | `[('is_company', '=', False), ('parent_id', '=', False)]` | Info |

*Adjust `total_due` / overdue fields to your localization (e.g. `credit` or custom fields).*

---

## Sale Order (`sale.order`)

| Name | Message | Conditions | Alert Style |
|------|---------|------------|-------------|
| Draft quotation | This is a draft quotation. Confirm to create the order. | `[('state', '=', 'draft')]` | Info |
| Large order | Large order: total **{amount_total}** (currency: {currency_id}). | `[('amount_total', '>', 10000)]` | Info |
| No order lines | This quotation has no order lines yet. | `[('order_line', '=', [])]` *or* `[('state', '=', 'draft')]` with message "Add order lines before confirming." | Warning |
| Quotation sent | Quotation has been sent. Waiting for confirmation. | `[('state', '=', 'sent')]` | Info |

*If `order_line = []` does not work in your version, use a rule with only `state = draft` and a message like "Draft – add lines and confirm when ready."*

---

## Purchase Order (`purchase.order`)

| Name | Message | Conditions | Alert Style |
|------|---------|------------|-------------|
| Draft RFQ | This is a draft request for quotation. | `[('state', '=', 'draft')]` | Info |
| Waiting approval | Purchase order is waiting for approval. | `[('state', 'in', ['to approve', 'draft'])]` | Warning |
| Large purchase | High value order: **{amount_total}**. | `[('amount_total', '>', 50000)]` | Info |

*Adjust state values to your workflow (e.g. `purchase.order` states: draft, sent, to approve, purchase, done, cancel).*

---

## Invoice / Bill (`account.move`)

| Name | Message | Conditions | Alert Style |
|------|---------|------------|-------------|
| Draft invoice | This is a draft invoice. | `[('state', '=', 'draft')]` | Info |
| Overdue | This invoice is overdue (invoice date in the past and not paid). | `[('payment_state', '!=', 'paid'), ('invoice_date_due', '<', context_today)]` *or* use a stored computed field for "overdue" | Danger |
| Large amount | Invoice total is **{amount_total}**. | `[('amount_total', '>', 10000)]` | Info |

*Overdue condition may require a computed/stored field on `account.move` (e.g. `is_overdue`) if domain cannot use `context_today`. Create a field that is True when `invoice_date_due < today` and `payment_state != 'paid'`, then use `[('is_overdue', '=', True)]`.*

---

## Stock Picking / Delivery (`stock.picking`)

| Name | Message | Conditions | Alert Style |
|------|---------|------------|-------------|
| Waiting availability | This delivery is waiting for stock. | `[('state', '=', 'waiting')]` | Warning |
| Partially available | Some lines are not fully available. | `[('state', '=', 'assigned')]` *optional: add partial qty check if you have a field* | Info |
| Not done | Delivery not yet done. Complete when shipped. | `[('state', 'not in', ['done', 'cancel'])]` | Info |

*State values: draft, waiting, confirmed, assigned, done, cancel – adjust to your workflow.*

---

## Quick copy-paste domains

```text
# Product variant: low stock
[('qty_available', '<', 10)]

# Product variant: out of stock
[('qty_available', '<=', 0)]

# Contact: no email or phone
['|', ('phone', '=', False), ('email', '=', False)]

# Sale order: draft
[('state', '=', 'draft')]

# Sale order: large amount (change 10000 to your threshold)
[('amount_total', '>', 10000)]

# Invoice: draft
[('state', '=', 'draft')]

# Purchase: draft or to approve
[('state', 'in', ['draft', 'to approve'])]
```

Create a new rule, set **Target Model** to the form where the warning should appear, paste the domain into **Conditions**, and write your **Warning Message**. Save and open a record that matches the conditions to test.
