# Smart CRM Task Generator | Create Project Tasks from Leads – Step-by-Step Setup

This guide explains how to install and configure the **crm_quick_task_advanced** module in Odoo 18 so you can create project tasks directly from Leads or Opportunities with pre-filled data (Subject, Project, Tags, Assignee, Customer).

---

## Step 1: Place the Module in Your Addons Path

1. Copy the `crm_quick_task_advanced` folder into a directory that is in your Odoo **addons path** (e.g. `addons` or a custom `project` addons directory).
2. Example structure:
   ```
   /path/to/odoo/
   ├── addons/           # or your custom addons folder
   │   └── crm_quick_task_advanced/
   │       ├── __manifest__.py
   │       ├── __init__.py
   │       ├── models/
   │       ├── views/
   │       ├── security/
   │       └── SETUP.md
   ```

---

## Step 2: Update the Apps List and Install the Module

1. Log in to Odoo as a user with **Administrator** rights.
2. Go to **Apps**.
3. Click **Update Apps List** (enable **Developer Mode** first if the button is hidden: Settings → Activate Developer Mode).
4. In the search box, type **Quick Task** or **crm_quick_task**.
5. Find **Smart CRM Task Generator | Create Project Tasks from Leads** and click **Install**.

---

## Step 3: Configure the Default Project (Sales & CRM Settings)

1. Go to **Settings**.
2. Open **Sales** (or **CRM**) and find the **Sales & CRM settings** (or **CRM** block).
3. Locate the setting **Quick Task Default Project**.
4. Select the **default project** to use when creating a Quick Task from a Lead or Opportunity (when no project is set on the Sales Team or on the Lead itself).
5. Click **Save**.

This project will be used as fallback when:
- The Lead/Opportunity has no **Quick Task Default Project** set, and  
- The Sales Team has no **Quick Task Default Project** set.

---

## Step 4: (Optional) Set Default Project per Sales Team

1. Go to **Sales** → **Configuration** → **Sales Teams** (or **CRM** → **Configuration** → **Sales Teams**).
2. Open a Sales Team (e.g. **Sales**, **Website Sales**).
3. In the form, find the **Quick Task** section.
4. Set **Quick Task Default Project** for this team.
5. Save.

Tasks created via Quick Task from Leads/Opportunities of this team will use this project by default (unless overridden on the Lead/Opportunity).

---

## Step 5: (Optional) Set Default Project on a Lead/Opportunity

1. Open any **Lead** or **Opportunity** (e.g. from **CRM** → **Leads** or **Opportunities**).
2. In the form, go to the **Tasks** tab (or the tab where Quick Task is shown).
3. If your view exposes it, you can set **Quick Task Default Project** on the Lead/Opportunity to override the team and global default for that record.

---

## Step 6: Create a Quick Task from a Lead or Opportunity

1. Open a **Lead** or **Opportunity** (e.g. **CRM** → **Opportunities** → open one record).
2. Go to the **Tasks** tab.
3. Click the **Quick Task** button (with the **+** icon).
4. The **Create Task** form opens with:
   - **Subject (Title)** = Lead/Opportunity name  
   - **Project** = default project (from settings, team, or lead)  
   - **Tags** = same tag names as on the Lead/Opportunity (mapped to Project tags)  
   - **Assignees** = salesperson of the Lead/Opportunity  
   - **Customer** = contact/partner of the Lead/Opportunity  
   - **Lead/Opportunity** = current record (link kept on the task)
5. Adjust any fields if needed and click **Save**.
6. The new task appears in **Project** → **Tasks** and in the **Tasks** tab of the Lead/Opportunity.

---

## Step 7: View Tasks Linked to a Lead/Opportunity

- On the Lead/Opportunity form, open the **Tasks** tab to see all tasks created from that record (Quick Tasks).
- On a **Project Task** form, the **Lead/Opportunity** field shows the source Lead or Opportunity, if the task was created via Quick Task.

---

## Summary of Configuration Order (Priority)

The **project** used for a Quick Task is chosen in this order:

1. **Lead/Opportunity** → **Quick Task Default Project** (if set)  
2. **Sales Team** → **Quick Task Default Project** (if set)  
3. **Settings** → **Sales & CRM** → **Quick Task Default Project** (if set)  
4. Otherwise, the first available project for the company is used (or an error is shown if none exists).

---

## Troubleshooting

- **“No default project set for Quick Task”**  
  Set at least one of: Quick Task Default Project in **Settings → Sales & CRM**, or on the **Sales Team**, or on the **Lead/Opportunity**. Ensure at least one **Project** exists.

- **Tasks tab or Quick Task button not visible**  
  Refresh the page, clear cache, and ensure the module is installed and the user has access to **CRM** and **Project**.

- **Tags not copied**  
  The module maps **CRM tag names** to **Project tags** by name; if a tag with the same name does not exist in Project, it is created. Ensure CRM tags are set on the Lead/Opportunity.

---

## Dependencies

- **crm**  
- **project**

Both are standard Odoo 18 modules and must be installed before **crm_quick_task_advanced**.
