# Step-by-Step Configuration with Multiple Data

This guide walks you through configuring the **Advanced Employee Attendance Report** module with multiple employees, departments, statuses, and report options.

---

## Table of Contents

1. [Prerequisites & Installation](#1-prerequisites--installation)
2. [Attendance Statuses (Multiple)](#2-attendance-statuses-multiple)
3. [Report Settings (Company Configuration)](#3-report-settings-company-configuration)
4. [Departments & Employees (Multiple Data)](#4-departments--employees-multiple-data)
5. [Attendance Data (Multiple Records)](#5-attendance-data-multiple-records)
6. [User Groups & Permissions (Multiple Users)](#6-user-groups--permissions-multiple-users)
7. [Reports & Dashboard (Multiple Filters)](#7-reports--dashboard-multiple-filters)
8. [Quick Reference: Sample Data Matrix](#8-quick-reference-sample-data-matrix)

---

## 1. Prerequisites & Installation

### 1.1 Install Python dependency

```bash
pip install xlsxwriter
```

### 1.2 Place module in addons path

- Copy folder `hr_attendance_report_advanced` into your Odoo addons directory.

### 1.3 Install in Odoo

1. Log in as **Administrator**.
2. Go to **Apps** → **Update Apps List** (if needed).
3. Search for **"Advanced Employee Attendance Report"**.
4. Click **Install**.

### 1.4 Verify menus

- **HR** → **Attendance** → **Attendance Reports** should show:
  - Generate Report  
  - Analytics Dashboard  
  - Matrix View  
  - Configuration (Attendance Statuses, Report Settings)

---

## 2. Attendance Statuses (Multiple)

The module loads **6 default statuses**. You can add more and edit existing ones.

### Step 2.1 Open Attendance Statuses

1. Go to **HR** → **Attendance** → **Attendance Reports** → **Configuration** → **Attendance Statuses**.

### Step 2.2 Default statuses (already created)

| Name     | Code | Color   | Use in reports      |
|----------|------|--------|---------------------|
| Present  | P    | Green  | Full day worked     |
| Half Day | H/F  | Blue   | Partial day         |
| Absent   | A    | Red    | Did not attend      |
| On Leave | L    | Pink   | Approved leave      |
| Week Off | WO   | Gray   | Weekend             |
| Holiday  | H    | Cyan   | Public holiday      |

### Step 2.3 Add a new status (e.g. "Work From Home")

1. Click **New**.
2. Fill in:
   - **Name:** Work From Home  
   - **Code:** WFH  
   - **Color:** `#6f42c1` (purple)  
   - **Sequence:** 25  
3. Set flags:
   - **Counts as Working:** ✓  
   - **Counts as Absent:** ☐  
   - **Counts as Leave:** ☐  
   - **Counts as Week Off:** ☐  
4. **Save**.

### Step 2.4 Add more statuses (examples)

- **Training** (code: TR, color: `#20c997`, Counts as Working).  
- **Sick Leave** (code: SL, color: `#fd7e14`, Counts as Leave).  
- **On Duty** (code: OD, color: `#ffc107`, Counts as Working).

Repeat **New** → fill name, code, color, sequence, flags → **Save** for each.

---

## 3. Report Settings (Company Configuration)

One configuration per company. If you have multiple companies, create one record per company.

### Step 3.1 Open Report Settings

1. Go to **HR** → **Attendance** → **Attendance Reports** → **Configuration** → **Report Settings**.

### Step 3.2 Create or edit configuration

- If the list is empty, click **New**.
- **Company** is set automatically to current company (change if multi-company).

### Step 3.3 Working hours (multiple scenarios)

| Field                         | Example 1 (Office) | Example 2 (Shift) | Example 3 (Part-time) |
|------------------------------|--------------------|-------------------|------------------------|
| Standard Working Hours/Day   | 8.0                | 12.0              | 4.0                    |
| Half Day Threshold (Hours)   | 4.0                | 6.0               | 2.0                    |
| Late Arrival Threshold (min) | 15                 | 10                | 15                     |
| Early Departure Threshold    | 15                 | 15                | 15                     |

Set the values that match your company policy.

### Step 3.4 Status colors

Use the same statuses as in **Attendance Statuses**; colors here are for reports/dashboard.

- **Present:** `#28a745`  
- **Absent:** `#dc3545`  
- **Half Day:** `#007bff`  
- **Leave:** `#fd7e14`  
- **Work On:** `#6c757d`  

Adjust if you added custom statuses and want different report colors.

### Step 3.5 Display & dashboard options

- **Default Date Range (Days):** e.g. 30 (for “last 30 days” default).  
- **Show Break Time / Overtime / Punctuality:** check as needed.  
- **Include Weekends / Holidays:** ✓ or ☐ per policy.  
- **Dashboard Refresh Interval:** e.g. 300 seconds or 0 to disable.  
- **Enable Attendance Alerts:** ✓ if you use alerts.

Save after each section if you do it in several steps.

---

## 4. Departments & Employees (Multiple Data)

Reports and dashboard filter by **Departments** and **Employees**. Set these up in HR.

### Step 4.1 Create multiple departments

1. Go to **HR** → **Configuration** → **Departments** (or **Employees** → **Departments**).
2. Create one record per department, for example:

| Department        | Manager (optional) |
|-------------------|--------------------|
| Management        | John Doe           |
| Research & Dev    | Jane Smith         |
| Sales             | Bob Wilson         |
| Support           | Alice Brown        |

### Step 4.2 Create multiple employees

1. Go to **HR** → **Employees**.
2. For each employee set:
   - **Name**  
   - **Department** (link to one of the departments above)  
   - **Work Contact** (optional)  
   - **User** (optional; for login and permissions)

Example:

| Employee   | Department        |
|-----------|-------------------|
| Marc Demo | Management       |
| Abigail   | Research & Dev    |
| Mitchell  | Management        |

### Step 4.3 (Optional) Department-level report/alert recipients

1. Open **HR** → **Configuration** → **Departments**.
2. Open a department (e.g. **Management**).
3. Find the **Attendance** tab (or similar from this module).
4. If the module adds **Attendance Alert Recipients** / **Report Recipients**, add one or more **Contacts** (partners) for alerts/reports.

Repeat for other departments if you use multiple recipients.

---

## 5. Attendance Data (Multiple Records)

Reports and dashboard need **hr.attendance** records (check-in/check-out).

### Step 5.1 Where to create attendance

- **HR** → **Attendance** → **Attendances** (or **Kiosk Mode** for self check-in/out).

### Step 5.2 Create multiple attendances (manual example)

1. Click **New**.
2. **Employee:** e.g. Marc Demo  
3. **Check In:** e.g. 2026-01-15 09:00  
4. **Check Out:** e.g. 2026-01-15 17:30  
5. **Attendance Status** (if the form has it): e.g. Present.  
6. Save.

Repeat for:

- Several dates (e.g. 1–20 Jan 2026).  
- Several employees (Marc, Abigail, Mitchell).  
- Different statuses (Present, Half Day, On Leave) where applicable.

### Step 5.3 Bulk / Kiosk

- Use **Kiosk Mode** so employees check in/out; that creates multiple attendance records automatically.
- Or use **Import** (if the module provides it) to upload CSV with multiple rows (employee, check-in, check-out, status).

### Step 5.4 What you should have for “multiple data”

- At least **2–3 departments**.  
- At least **3–5 employees** in different departments.  
- At least **10–20 attendance lines** across different employees and dates.

---

## 6. User Groups & Permissions (Multiple Users)

Configure who can see reports, dashboard, and configuration.

### Step 6.1 Open groups

1. Go to **Settings** → **Users & Companies** → **Groups**.
2. Search: **Attendance Report**.

You should see:

- **Attendance Report User**  
- **Attendance Report Manager**  
- **Attendance Report Administrator**

### Step 6.2 Assign groups to multiple users

1. Go to **Settings** → **Users & Companies** → **Users**.
2. Open **User A** (e.g. HR manager):
   - **Access Rights** tab → add **Attendance Report Manager**.
3. Open **User B** (e.g. department head):
   - Add **Attendance Report User** (or Manager if they must export/analytics).
4. Open **User C** (e.g. admin):
   - Add **Attendance Report Administrator** if they must change configuration.

Summary:

| Group        | Typical use                         |
|-------------|--------------------------------------|
| User        | View and generate reports            |
| Manager     | User + analytics, export, more data   |
| Administrator | Manager + configuration, all settings |

### Step 6.3 Multi-company (optional)

- If you have **multiple companies**, set each user’s **Allowed Companies** and create **Report Settings** per company (Step 3.2).  
- Reports will respect the current company and its configuration.

---

## 7. Reports & Dashboard (Multiple Filters)

Use **multiple** date ranges, employees, and departments to see different slices of data.

### Step 7.1 Generate Report (multiple filters)

1. **HR** → **Attendance** → **Attendance Reports** → **Generate Report**.
2. **Report Type:** e.g. Detailed Report / Summary Report / Combined / Matrix View.
3. **From Date** / **To Date:** e.g. 01/12/2025 – 31/01/2026.
4. **Employees:**  
   - Leave empty = all employees.  
   - Or select multiple: Marc Demo, Abigail, Mitchell.
5. **Departments:**  
   - Leave empty = all.  
   - Or select one or more: Management, Research & Dev.
6. **Group By:** Employee or Department (for grouped totals).
7. **Output Format:** PDF or Excel.
8. Click **Generate Report**.

Try different combinations:

- One department only.  
- Multiple employees, one department.  
- All employees, all departments.  
- Different date ranges (e.g. last week, last month, custom range).

### Step 7.2 Analytics Dashboard (multiple data)

1. **HR** → **Attendance** → **Attendance Reports** → **Analytics Dashboard**.
2. Set **From Date** and **To Date**.
3. **Employees:** leave empty or select multiple.
4. **Departments:** leave empty or select multiple.
5. Click **Refresh Dashboard**.

You should see:

- **Key Performance Indicators** (totals/averages).  
- **Daily Attendance Trends** (table).  
- **Department Attendance Rates** (table).  
- **Punctuality** and **Overtime** (lists).  
- **Current Employee Status** (checked in/out).

Change filters (dates, employees, departments) and click **Refresh Dashboard** again to compare different “multiple data” sets.

### Step 7.3 Matrix View

1. **HR** → **Attendance** → **Attendance Reports** → **Matrix View**.
2. Set date range and optionally **Employees** / **Departments**.
3. Click **Refresh Matrix** (if the button exists) or open the view.

Matrix shows one row per employee and columns per day; use it with multiple employees and dates for a quick overview.

---

## 8. Quick Reference: Sample Data Matrix

Use this as a checklist for “multiple data” configuration.

| Item              | Minimum for testing | Example                          |
|-------------------|---------------------|----------------------------------|
| Companies         | 1 (or 2 for multi)  | YourCompany                      |
| Report configs    | 1 per company       | 1 record in Report Settings      |
| Attendance statuses | 5–6 default + 1–2 custom | Present, Absent, Half Day, Leave, WFH |
| Departments       | 2–4                 | Management, R&D, Sales, Support  |
| Employees         | 3–5                 | Marc, Abigail, Mitchell, …       |
| Attendance records| 10–30               | Mix of employees and dates       |
| Users with access | 2–3                 | 1 User, 1 Manager or Admin       |
| Report runs       | 3–5                 | Different filters each time      |

---

## Troubleshooting (Multiple Data)

- **No data in report/dashboard:**  
  - Check **From/To** date.  
  - Confirm **attendances** exist for that range (**HR** → **Attendance**).  
  - If you filtered by **Employees** or **Departments**, ensure they have attendances in the period.

- **Wrong totals:**  
  - Check **Report Settings** (working hours, half-day threshold).  
  - Ensure **Attendance Status** on records matches your statuses (Present, Half Day, etc.).

- **Some employees/departments missing:**  
  - Verify **Employees** are active and have **Department** set.  
  - In the report wizard, leave **Employees** and **Departments** empty once to see “all” and compare.

- **Permission errors:**  
  - Assign the correct **Attendance Report** group (User / Manager / Administrator) under **Settings** → **Users** → **Access Rights**.

---

**You now have step-by-step configuration with multiple statuses, departments, employees, attendance records, users, and report/dashboard filters.**
