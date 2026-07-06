# Remittance Advice (Odoo 18)

This module adds **Remittance Advice** generation and email for **Vendor Payments**: print a PDF and/or send it by email with optional company signature.

---

## Features

- **Remittance Advice Report (PDF)** – Print from Vendor Payments (Print → Remittance Advice (PDF)).
- **Company Signature** – Signature image from Company settings is shown on the report.
- **Send Remittance Advice by Email** – Use “Send receipt by email” with Remittance Advice template and PDF attached when the option is enabled.
- **Remittance Advice configuration** – On each Vendor Payment you can enable “Remittance Advice” and choose an email template; when enabled, the composer uses that template and attaches the Remittance Advice PDF.

---

## Installation

1. Copy the `remittance_advice` folder into your Odoo addons path (e.g. next to `odoo/addons` or in a custom addons directory).
2. Update the app list: **Apps** → **Update Apps List**.
3. Search for **Remittance Advice** and click **Install**.

---

## Step-by-step configuration

### 1. Company signature (optional)

1. Go to **Settings** → **Companies** → open your company (or **Invoicing** → **Configuration** → **Companies** → open company).
2. In the company form, find **Company Signature** (below Company Registry).
3. Click the field and upload a signature image (PNG/JPEG).
4. Save.

This image is used on the Remittance Advice PDF when available.

### 2. Remittance Advice email template (default)

The module installs a default template **“Remittance Advice (Vendor Payments)”**:

1. Go to **Settings** → **Technical** → **Email** → **Email Templates** (or **Invoicing** → **Configuration** → **Email Templates** if you have that menu).
2. Search for **“Remittance Advice”**.
3. Open **“Remittance Advice (Vendor Payments)”**.
4. You can edit:
   - **Subject** (e.g. `Remittance Advice for {{ object.name }}`)
   - **Body**
   - **Report** (should already be set to attach the Remittance Advice report).

The template is linked to the **Remittance Advice** report so the PDF is attached automatically when sending.

### 3. Vendor payment – enable Remittance Advice

1. Go to **Accounting** → **Vendors** → **Vendor Payments** (or **Invoicing** → **Vendors** → **Payments**).
2. Open or create a **Vendor Payment** (partner type = Vendor).
3. In the form, find the **“Remittance Advice Configuration”** section (only visible for Vendor Payments).
4. Check **Remittance Advice**.
5. Optionally set **Remittance Advice Email Template** (if empty, the default “Remittance Advice (Vendor Payments)” template is used).
6. Save.

From now on, when you use **“Send receipt by email”** on this payment, the composer will use the Remittance Advice template and attach the Remittance Advice PDF.

---

## Step-by-step data creation and usage

### A. Create a vendor and a bill

1. **Create vendor** (if needed): **Contacts** → **Create** → set **Company** and **Vendor**.
2. **Create a bill**: **Accounting** → **Vendors** → **Bills** → **Create**:
   - Vendor, product/service, quantity, price.
   - Confirm and **Register Payment** (or leave unpaid and pay later).

### B. Register a vendor payment

1. **Accounting** → **Vendors** → **Vendor Payments** → **Create**.
2. Fill:
   - **Payment Type**: Send money.
   - **Vendor**: your vendor.
   - **Amount**, **Journal**, **Payment Method**, etc.
3. In **Remittance Advice Configuration**:
   - Check **Remittance Advice**.
   - Optionally choose **Remittance Advice Email Template** (or leave default).
4. **Confirm** the payment.
5. If you have open bills for this vendor, **reconcile**: use **Reconcile** or **Register Payment** from the bill so this payment is linked to the bill(s).

### C. Print Remittance Advice (PDF)

1. Open the **Vendor Payment**.
2. Click **Print** (dropdown).
3. Choose **Remittance Advice (PDF)**.
4. The PDF opens with payment details, reconciled bills table, and company signature (if set).

### D. Send Remittance Advice by email

1. Open the **Vendor Payment**.
2. Click **Action** → **Send receipt by email** (or the equivalent “Send receipt by email” action).
3. The composer opens with:
   - **Template**: Remittance Advice (Vendor Payments) (or the one you set on the payment).
   - **Attachments**: Remittance Advice PDF added automatically.
4. Set **Recipients** (and adjust subject/body if needed).
5. Click **Send**.

When **Remittance Advice** is **unchecked** on the payment, “Send receipt by email” uses the standard Odoo payment receipt template and its attachment instead.

---

## Technical notes

- **Report**: `remittance_advice.report_remittance_advice` (only for `account.payment` with `partner_type = 'supplier'`).
- **Company signature**: `res.company.company_signature` (Binary).
- **Payment fields**: `remittance_advice` (Boolean), `remittance_advice_template_id` (Many2one to `mail.template`).
- **Composer**: `mail.compose.message` is extended so that when opening “Send receipt by email” for vendor payments with Remittance Advice enabled, the default template is set to the Remittance Advice template (and the report is attached via the template’s **Report** setting).

---

## Version

- **Odoo**: 18.0  
- **Module version**: 18.0.1.0.0
