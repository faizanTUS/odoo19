# Material Requisition & Inventory Management with Purchase Workflow

Material Purchase Requisitions and Internal Picking Requisitions by Employee/User, with department manager and requisition officer approval, email notifications, and user default stock location.

---

## Step-by-Step Configuration

### 1. Install the Module

- Go to **Apps**, search for **Material Requisition**.
- Click **Install**.

### 2. Configure Approval Workflow

- Go to **Inventory → Material Requisition → Configuration**.
- Set:
  - **Send Email Notifications for Approval**: Enable to send emails to department manager and requisition officer.
  - **Require Department Manager Approval**: Enable so requisitions wait for department manager before officer.
  - **Require Requisition Officer Approval**: Enable so requisitions need officer approval before creating pickings/POs.
  - Click **Save**.

### 3. Assign Department Managers

- Go to **Employees → Configuration → Departments**.
- Open each department.
- Set **Manager** to the user who should approve requisitions for that department.
- The linked user will receive approval emails and see **Approve** / **Reject** on confirmed requisitions.

### 4. Assign Requisition Officers

- Go to **Settings → Users & Companies → Users**.
- Open a user who will act as requisition officer.
- In **Access Rights** (or the page where user fields are), find **Material Requisition**:
  - Check **Requisition Officer**.
  - Optionally set **User Stock Location** (default destination for requisitions when not set on the form).
- Save.

### 5. (Optional) User Default Stock Location

- In **Settings → Users & Companies → Users**, for each employee (or requisition officer) you can set **User Stock Location**.
- When a material requisition is created and **Destination Location** is empty, this location is used as default.

### 6. Configure Picking Types (for Internal Picking)

- Go to **Inventory → Configuration → Operation Types**.
- Ensure you have an **Internal Transfer** type (code: internal) per warehouse.
- Requisition lines with **Requisition Action = Internal Picking** will need a **Picking Type** (and optionally **Warehouse**) set by the requisition officer before generating pickings.

---

## Step-by-Step: Create a Material Requisition (Entry)

### As Employee

1. Go to **Inventory → Material Requisition**.
2. Click **New**.
3. Fill:
   - **Request Date**: Default is today.
   - **Requested By**: Filled with current user.
   - **Department**: Filled from your employee record if linked.
   - **Source Location** / **Destination Location**: Optional; if empty, destination can default from your **User Stock Location** (if set).
   - **Requisition Type**: Purchase / Internal / Both (informational).
4. In **Requisition Lines** add lines:
   - **Product**, **Required Quantity**, **UoM**.
   - **Requisition Action**:
     - **Purchase Order**: will create RFQ/PO to vendor (vendor must be set on line by officer).
     - **Internal Picking**: will create an internal transfer (picking type must be set on line by officer).
   - **Purchase Order Price** (optional).
5. Click **Confirm Request**.

### As Department Manager

1. You receive an email (if notifications are on) or open **Inventory → Material Requisition** and filter by **Confirmed**.
2. Open the requisition.
3. Click **Approve** or **Reject**.
4. If you **Reject**, enter a reason in the wizard and confirm.

### As Requisition Officer

1. You receive an email (if notifications are on) or open **Inventory → Material Requisition** and open a requisition in **Confirmed** or **Approved by Department Manager**.
2. Set **Destination Location** (and **Source Location** if needed) on the header.
3. On each line:
   - For **Internal Picking**: set **Warehouse** and **Picking Type**.
   - For **Purchase Order**: set **Vendor** (and **Purchase Order Price** if needed).
4. Click **Approve**.
5. Then:
   - **Create Picking**: creates internal transfer(s) for lines with **Requisition Action = Internal Picking**.
   - **Create Purchase Order**: creates RFQ/PO(s) per vendor for lines with **Requisition Action = Purchase Order**.
6. After creating pickings/POs, status moves to **Dispatch**.

### As Employee (Receive)

1. When materials are dispatched, open the requisition (state **Dispatch**).
2. Click **Received** when you have received the materials at your location.

### Other Actions

- **Print Material Requisition**: Use **Print** (dropdown) and choose **Material Requisition (PDF)** for the PDF report.
- **Reset to Draft**: Only for **Draft** or **Rejected**; clears approvals and rejection so you can edit and confirm again.

---

## Roles Summary

| Role | Capabilities |
|------|--------------|
| **Employee** | Create requisitions, add lines, confirm, print PDF, mark Received. Sees only own requisitions. |
| **Department Manager** | Approve or reject requisitions of their department. |
| **Requisition Officer** | Set destination/source, add vendor and picking type on lines, approve/reject, create pickings and POs, print PDF. |

---

## Features Covered

- Employees create material requisition requests; multiple lines per form.
- Employees see only their own records (record rules).
- Department manager approval/decline.
- Requisition officer approval/reject; destination location; vendor and picking details per line.
- Per-line **Requisition Action**: **Purchase Order** (RFQ/PO to vendor) or **Internal Picking** (internal transfer).
- Email notifications to department manager and requisition user for approval (configurable).
- User default stock location for requisition destination.
- PDF report with signatures (Prepared By, Approved By Department Manager, Approved By Requisition Officer).
- **Received** button for employees when materials are received.

---

## Technical Notes

- **Models**: `material.requisition`, `material.requisition.line`, `material.requisition.config`, `material.requisition.reject.wizard`; extends `res.users`, `stock.picking`.
- **Security**: Groups `group_material_requisition_user`, `group_material_requisition_manager`, `group_material_requisition_officer`; record rules for employee (own) and manager (department); officer sees all.
- **Sequence**: `MR/` prefix for requisition reference.
- **Reports**: `action_report_material_requisition` (PDF).
