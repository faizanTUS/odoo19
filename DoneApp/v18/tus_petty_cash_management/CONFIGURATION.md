# Petty Cash Pro — Step-by-step configuration

This guide walks you from a fresh database to a working petty cash setup with **example values** you can copy or adapt.

---

## 1. Server: add the addon path

Point Odoo at the folder that contains `tus_petty_cash_management` (for this project that is `project/`).

**Example** (`odoo.conf` or your environment file):

```ini
[options]
addons_path = /home/tus/workspace/odoo18/odoo/addons,/home/tus/workspace/odoo18/project
```

Restart the Odoo service after changing `addons_path`.

---

## 2. Install the module

1. Enable **Developer mode** (Settings).
2. **Apps** → Update Apps List.
3. Remove **Apps** filter, search **Petty Cash Pro**.
4. Click **Install**.

Optional **demo data**: create the database with demo data enabled, or install with demo so the module loads `data/petty_cash_demo.xml` and the **post-install hook** can create a sample fund, approval tiers, and a draft voucher (requires a cash journal and HR employee in the company).

---

## 3. Security groups

| Group | Purpose |
|--------|---------|
| **Petty Cash / User** | Create and follow own vouchers; see funds and policies as configured. |
| **Petty Cash / Manager** | Full configuration, approve/pay, replenishment posting, all vouchers. |

**Settings → Users & Companies → Users**: add **Petty Cash → Manager** (or User) to each person who should use the app.

---

## 4. Chart of accounts (prerequisites)

Before creating a fund you need to ensure your accounts are correctly typed in **Accounting → Configuration → Chart of Accounts**.

### 4a. Account Configuration Details

| Account Code | Account Name | **Correct Type** | Notes |
| :--- | :--- | :--- | :--- |
| **101501** | `Petty Cash - Main` | **Bank and Cash** | Liquidity account for the Cash Journal. |
| **601001** | `Office` | **Expense** | **CRITICAL:** Do NOT use "Bank and Cash" for expense accounts. |
| **602001** | `Travel` | **Expense** | Linked to Travel Category. |

> **IMPORTANT:** If an expense account is incorrectly set to "Bank and Cash", Odoo will treat petty cash vouchers as internal transfers rather than spending. This will hide the expenses from your Profit & Loss reports and inflate your balance sheet.

| Item | Example | Notes |
|------|---------|--------|
| **Petty cash GL account** | `101501 Petty Cash – Main` | One account per fund is clearest. |
| **Expense accounts** | `601001 Office`, `602001 Travel` | Linked to **Expense categories** in Petty Cash. |
| **Petty cash journal** | `PCSH1 Main petty cash` | Type **Cash**. |
| **Bank journal** | `BNK1` | Used for replenishment (topping up the fund). |

Create these under **Accounting → Configuration → Chart of Accounts / Journals** if they do not exist yet.



Configure your accounts under **Accounting → Configuration → Chart of Accounts**.

| Account Code | Account Name | **Correct Type** | Notes |
| :--- | :--- | :--- | :--- |
| **101501** | `Petty Cash - Main` | **Bank and Cash** | Liquidity account for the Cash Journal. |
| **601001** | `Office` | **Expense** | **CRITICAL:** Do NOT use "Bank and Cash" for expense accounts. |
| **602001** | `Travel` | **Expense** | Linked to Travel Category. |

> **Note:** If an expense account is incorrectly set to "Bank and Cash", Odoo will treat vouchers as internal transfers rather than actual spending, which will break your Profit & Loss reports.


---

## 5. Expense categories

**Petty Cash → Configuration → Expense Categories**

Example rows:

| Name | Code | Expense account |
|------|------|-----------------|
| Office supplies | `OFF` | Office expense account |
| Transport | `TRN` | Travel / fuel account |

---

## 6. Spend policy

**Petty Cash → Configuration → Spend Policies**

Example policy **“Standard Petty Cash Policy”**:

| Field | Example value |
|--------|----------------|
| Max amount per voucher | `500.00` |
| Daily limit per employee | `200.00` |
| Monthly limit per employee | `2000.00` |
| Require receipt | ✓ (flags missing attachments on the dashboard) |
| Allowed categories | Office supplies, Transport |

---

## 7. Petty cash fund

**Petty Cash → Funds → Create**

| Field | Example |
|--------|---------|
| Name | `Main Office Petty Cash` |
| Code | `PC-MAIN` |
| Custodian | User responsible for the physical cash box |
| Spend policy | Standard Petty Cash Policy |
| Petty cash journal | `PCSH1` |
| Petty cash GL account | Same as petty cash account line (cash box) |
| Default expense account | Fallback if a category has no account |
| Replenishment source journal | `BNK1` |
| Minimum balance (alert) | `150.00` |
| Suggest replenishment | ✓ |
| Replenishment target amount | `500.00` |

### Approval matrix (same form, tab **Approval matrix**)

Example tiers (amounts are **inclusive** on the upper bound):

| Sequence | Name | Amount from | Amount to | Approver |
|----------|------|-------------|-----------|----------|
| 10 | Tier 1 | `0.00` | `150.00` | Department manager |
| 20 | Tier 2 | `150.01` | `999999.00` | Finance manager |

Save the fund.

---

## 8. End-to-end voucher flow (example)

1. **Petty Cash → Vouchers → Create**  
   - Fund: `Main Office Petty Cash`  
   - Employee: requester  
   - Category: `Office supplies`  
   - Amount: `45.00`  
   - Description: `Client visit – coffee and supplies`  
   - Attach a receipt (if policy requires).

2. **Submit** → state **Under approval** (approval lines appear).

3. **Approver** (logged in as **Current approver**) → **Approve** (or **Reject** with reason).

4. **Manager** → **Register payment** → journal entry posted (expense **Debit**, petty cash **Credit**).

5. **Mark reconciled** when matched with bank/cash control.

---

## 9. Replenishment (example)

When balance is low:
   
1. Open the **fund** → **Request replenishment** (or **Petty Cash → Replenishments**).
2. Amount: `500.00` → **Submit** → **Approve** → **Post** → GL: **Petty cash Debit**, **Bank Credit**.

---

## 10. Reporting and exports

| Need | Where |
|------|--------|
| KPIs | **Petty Cash → Dashboard** |
| Open pipeline | **Petty Cash → Reporting → Aging Analysis** |
| PDF | Select vouchers → **Print** → **Petty Cash Aging (PDF)** |
| Excel-friendly CSV | List view → **Action** → **Petty Cash Aging Report (Excel CSV)** |

---

## 11. Demo data summary (when installing with demo)

| Record | Description |
|--------|----------------|
| Categories | Office Supplies (`OFF`), Transport (`TRN`) |
| Policy | Standard Petty Cash Policy (limits + receipt required) |
| Hook (if COA + cash journal exist) | **Main Office Petty Cash (Demo)** fund, two approval tiers, one **draft** voucher |

If the hook does not create the fund (no cash journal, etc.), complete **sections 4–7** manually using the tables above.

---

## 12. Sample `addons_path` for this workspace only

This repository already uses `project/` in `conf/app_18e.conf`. To run Odoo with the same layout:

```ini
addons_path = /home/tus/workspace/odoo18/odoo/addons,/home/tus/workspace/odoo18/enterprise,/home/tus/workspace/odoo18/project
```

Adjust paths to match your machine.
