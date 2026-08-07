# RMA Management - Step-by-Step Setup Guide

This guide details the configuration and workflow for the Return Merchandise Authorization (RMA) module in Odoo 18.

---

## Phase 1: Installation & Configuration

### 1. Module Installation
1. Ensure the module `rma_management` is in your custom addons path.
2. Update the Apps List: **Apps > Update Apps List**.
3. Search for `RMA Management` and click **Activate**.

### 2. Security Roles
Go to **Settings > Users & Companies > Users**, select a user, and assign:
- **RMA User**: Can create and process RMA requests.
- **RMA Manager**: Full access to configuration (Reasons, Fees, Types).

---

## Phase 2: Master Data Entry (Configuration)

Before processing returns, you must define your business rules.

### Step 1: Create RMA Reasons
**Menu**: RMA Management > Configuration > Reasons
These define why a customer is returning a product and what the default action should be.

| Field | Example Entry |
| :--- | :--- |
| **Reason** | Defective / Damaged |
| **Action** | Replacement |

*Note: Actions include `Replacement`, `Refund`, `Return Only`, or `Refund (No Return)`.*

### Step 2: Create Restocking Fees
**Menu**: RMA Management > Configuration > Restock Fees
Used to deduct a handling fee from the refund amount.

| Field | Example Entry |
| :--- | :--- |
| **Name** | Standard 15% Handling Fee |
| **Type** | Percentage |
| **Amount** | 15.00 |

### Step 3: Define RMA Product Types
**Menu**: RMA Management > Configuration > Product Types
Categorize products for RMA reporting (e.g., Electronics, Fragile).

---

## Phase 3: Product Setup

To enable RMA features on a product:
1. Open **Sales > Products** and select a product.
2. Go to the **Inventory** tab.
3. Locate the **RMA Configuration** group:
   - **RMA Product Type**: Select a type (e.g., Electronics).
   - **RMA Threshold**: Enter a quantity (e.g., `5.0`). *Prevents RMA if total order qty is below this.*

---

## Phase 4: Transactional Workflow (Creating Records)

### Workflow Example: Customer Return Request

#### 1. Creating the RMA Record
**Menu**: RMA Management > Customer RMA > Returns > New
1. **Customer**: Select `Azure Interior`.
2. **Sale Order**: Select `S00015`.
3. **RMA Lines**: Click `Add a line`.
   - **Product**: `Office Chair`.
   - **Return Qty**: `1`.
   - **Reason**: `Defective`.

#### 2. Processing the RMA
1. **Submit**: Click **Submit** to move the state from `Draft` to `Submitted`. (Sends an automated notification).
2. **Approve**: After inspection, click **Approve**.
3. **Receipt**: Click **Generate Picking** to create an Incoming Shipment to bring the item back.
4. **Action**: Click **Execute Action**.
   - If the reason was `Replacement`, Odoo creates a new Delivery Order.
   - If the reason was `Refund`, Odoo creates a Draft Credit Note.

---

## Phase 5: Odoo 18 XML Record Examples

If you want to create default records via data files, use the following syntax:

### Example: RMA Reason (XML)
```xml
<record id="reason_wrong_color" model="rma.reason">
    <field name="name">Wrong Color Received</field>
    <field name="action">replacement</field>
</record>
```

### Example: Mail Template (Odoo 18 Syntax)
```xml
<record id="email_template_rma_approved" model="mail.template">
    <field name="name">RMA Approved</field>
    <field name="model_id" ref="rma_management.model_customer_rma"/>
    <field name="subject">Your RMA {{ object.name }} has been Approved</field>
    <field name="body_html" type="html">
        <div style="margin: 0px; padding: 0px;">
            <p>Dear <t t-out="object.partner_id.name"/>,</p>
            <p>Your return request <b><t t-out="object.name"/></b> is approved.</p>
        </div>
    </field>
</record>
```
