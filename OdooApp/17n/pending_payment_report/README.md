# Pending Payment Report - Odoo 18

This module allows you to generate an **Excel report of outstanding invoices/bills** from the Pending Payment Report wizard. Data is **grouped by Customer/Vendor**. The report includes **currency wise total** and **Grand total**, **receive amount with date**, and you can **auto-send** the pending payment report to a **configured user** by email.

---

## Features

- Generate **Pending Payment Excel report** of invoices and/or bills from the wizard.
- Report data **grouped by Customer/Vendor** (and by Type when both invoices and bills are selected).
- **Multiple filters**: Start Date, End Date, Due Date From/To, Customer/Vendor, Currency, Company, Salesperson.
- Generate report for **Invoices only**, **Bills only**, or **Both** in one report.
- **Received amount with payment date(s)** shown in the Excel and in the detail view.
- **Currency wise total** and **Grand total** in the Excel report.
- **Auto-send** pending payment report (Excel) by email to a **configured user** (set in Settings).

---

## Why "No pending payment data found for the selected filters"?

The report only includes **posted** customer invoices or vendor bills that are **not fully paid** (payment state **Not Paid** or **Partial**) and whose **Due Date** is **within** the range you set (Due Date From / Due Date To). If you have no such records, you get this message. Follow the configuration and data setup below to create sample data.

---

## Configuration and Data Setup (Step by Step)

Follow these steps so the Pending Payment Report has data to show.

### A. Prerequisites (one-time)

1. **Company and accounting**
   - Your company must have a **Chart of Accounts** (Invoicing → Configuration → Settings → set Fiscal Localization if needed).
   - You need at least one **Sales Journal** (for customer invoices) and/or **Purchase Journal** (for vendor bills). These are usually created with the chart of accounts.

2. **Product**
   - **Invoicing** → **Products** → **Create**: add at least one sellable product (e.g. "Service" or "Product A"), with a **Sales Price**.

3. **Customer (for Customer Invoices)**
   - **Invoicing** → **Customers** → **Create**.
   - Name: e.g. "Customer Alpha".
   - Save.

4. **Vendor (for Vendor Bills, optional)**
   - **Invoicing** → **Vendors** → **Create**.
   - Name: e.g. "Vendor Beta".
   - Save.

---

### B. Create a customer invoice (so it appears in the report)

1. **Invoicing** → **Customers** → **Invoices** → **Create**.
2. **Customer**: Select "Customer Alpha" (or your customer).
3. **Invoice Date**: e.g. today or any date.
4. **Due Date**: Set a date that will fall **inside** the range you will use in the report (e.g. if you will use Due Date From = 2025-01-01 and Due Date To = 2025-12-31, set Due Date = 2025-06-15).
5. Add an **Invoice Line**: product = your product, quantity = 1, unit price as needed.
6. **Save**.
7. Click **Confirm** (post the invoice). Status should be **Posted**.
8. **Do not register a full payment** for this invoice (leave it **Not Paid**, or register a partial payment so it stays **Partial**).

Your invoice is now:
- **Posted**
- **Not Paid** or **Partial**
- **Due Date** within your future report range  
→ It will appear in the Pending Payment Report when you use that due date range.

---

### C. Create a vendor bill (optional, for "Vendor Bills" or "Both")

1. **Invoicing** → **Vendors** → **Bills** → **Create**.
2. **Vendor**: Select "Vendor Beta" (or your vendor).
3. **Bill Date**: any date.
4. **Due Date**: Set a date **inside** the same range you will use in the report (e.g. 2025-07-01).
5. Add a **Bill Line**: product (purchasable) or description + amount.
6. **Save** → **Confirm** (post the bill).
7. **Do not pay** the bill fully (leave **Not Paid** or **Partial**).

---

### D. Run the Pending Payment Report with the correct filters

1. Go to **Invoicing** → **Reporting** → **Pending Payment Report** → **Pending Payment Report**.
2. Set:
   - **Due Date From**: first day of the range that **includes** your invoice/bill due dates (e.g. **01/01/2025**).
   - **Due Date To**: last day of that range (e.g. **31/12/2025**).
   - **Invoice Type**: **Customer Invoices Only** (if you only created an invoice), or **Vendor Bills Only** (if you only created a bill), or **Both Invoices and Bills**.
   - Leave **Customer / Vendor** empty to see all, or select one partner.
3. Click **View Report** or **Print Excel**.

You should now see at least one line (your customer or vendor with pending amount).

---

### E. Quick checklist when the report is empty

| Check | What to do |
|-------|------------|
| Invoices/bills are **Draft**? | **Confirm** them (Post) so status = Posted. |
| Invoices/bills are **fully paid**? | Leave at least one invoice/bill **Not Paid** or **Partial**. |
| **Due Date** outside your range? | Set Due Date From/To in the wizard so they **include** the due dates of your invoices/bills. |
| **Wrong Invoice Type**? | For customer invoices choose "Customer Invoices Only"; for vendor bills choose "Vendor Bills Only" or "Both". |
| **Wrong Company**? | In the wizard, select the same **Company** that owns the invoices/bills (in multi-company). |

---

## Step-by-Step Configuration

### 1. Install the module

1. Place the `pending_payment_report` folder in your Odoo addons path (e.g. `addons/` or `project/`).
2. Restart Odoo.
3. Go to **Apps** → **Update Apps List**.
4. Search for **Pending Payment Report**.
5. Click **Install**.

**From command line:**

```bash
./odoo-bin -c odoo.conf -i pending_payment_report --stop-after-init
```

### 2. Configure the recipient for auto-send (optional)

To use **Send to Configured User** and auto-send the report by email:

1. Go to **Invoicing** (or **Accounting**) → **Configuration** → **Pending Payment Report Settings**.
2. In **Auto-send report to**, select the **Partner** (or user’s partner) who should receive the report.
3. Click **Save**.

That partner must have an **email** set; otherwise the send will fail.

### 3. Open the Pending Payment Report wizard

1. Go to **Invoicing** → **Reporting** → **Pending Payment Report** → **Pending Payment Report**.
2. The wizard opens with filters.

### 4. Set filters and generate the report

**Filters:**

- **Customer / Vendor**: Leave empty for all, or select one partner.
- **Start Date** / **End Date**: Optional. Filter by invoice/bill date.
- **Due Date From** / **Due Date To**: **Required.** Filter by due date.
- **Currency**: Leave empty for all currencies, or select one.
- **Company**: Default is current company (for multi-company).
- **Sale Person**: Leave empty for all, or select one.
- **Invoice Type**:
  - **Customer Invoices Only**
  - **Vendor Bills Only**
  - **Both Invoices and Bills** (one report with Type column)

**Actions:**

- **View Report**: Builds the report and opens the tree view (grouped by Customer/Vendor, with Type if “Both” was selected). From the tree you can use **Send Email** to send pending payment details to selected customers.
- **Print Report**: Generates a PDF report.
- **Print Excel**: Downloads an Excel file with:
  - Rows grouped by Customer/Vendor (and Type when “Both”).
  - Columns: Customer/Vendor, Type (if both), Currency, Total, Received Amount, Payment Date(s), Pending Amount, Invoice Count, Email ID.
  - **Currency wise total** rows (e.g. “Total (USD)”, “Total (EUR)”).
  - **Grand Total** row at the end.
- **Send to Configured User**: Generates the same Excel report and **sends it by email** to the partner configured in **Settings** (see step 2). Use this for auto-send to a configured user.

### 5. Excel report content

- **Received amount** = paid amount per line.
- **Payment Date(s)** = dates of reconciled payments for that line (from invoice/bill payments).
- **Currency wise total**: After all data rows, one row per currency with totals.
- **Grand Total**: Last row with overall totals.

### 6. Sending emails to customers (from tree view)

1. In the wizard, click **View Report**.
2. In the tree view, select the rows (customers/vendors) you want to email.
3. Click **Send Email** in the list header.
4. Compose the email (template “Pending Payment Details” is used) and send.

### 7. Customize email templates (optional)

- **Pending Payment Details** (for customers): **Settings** → **Technical** → **Email** → **Templates**. Find “Pending Payment Details” (model: Pending Payment Report Line). Edit subject/body.
- **Report to configured user**: Template “Pending Payment Report (To Configured User)” (model: Pending Payment Report Wizard). Used when you click **Send to Configured User**.

### 8. Excel export dependency

The **Print Excel** and **Send to Configured User** actions require the **xlsxwriter** Python package:

```bash
pip install xlsxwriter
```

Then restart Odoo.

---

## Summary

| Feature | Description |
|--------|-------------|
| Excel report | Outstanding invoices/bills, grouped by Customer/Vendor |
| Filters | Start date, End date, Due date, Customer/Vendor, Currency, Company, Salesperson, Invoice type |
| Invoice type | Invoices only, Bills only, or Both |
| Receive amount with date | Received amount and payment date(s) in Excel and detail view |
| Currency total & Grand total | Per-currency totals and grand total in Excel |
| Auto-send to configured user | Configure recipient in Settings; use “Send to Configured User” in wizard |

---

## Troubleshooting

- **No data in report** (message "No pending payment data found for the selected filters"): Follow **Configuration and Data Setup (Step by Step)** above. Ensure invoices/bills are **posted**, **Not Paid** or **Partial**, and due date is **within** Due Date From/To.
- **Send to Configured User fails**: Set **Auto-send report to** in Invoicing → Configuration → Pending Payment Report Settings and ensure that partner has an email.
- **Excel export error**: Install `xlsxwriter` and restart Odoo.
