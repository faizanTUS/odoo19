# Advanced Approval Workflow - Configuration Guide

## Table of Contents
1. [Installation](#installation)
2. [User Groups Setup](#user-groups-setup)
3. [Creating Approval Types](#creating-approval-types)
4. [Configuring Approval Lines](#configuring-approval-lines)
5. [Creating Approval Requests](#creating-approval-requests)
6. [Approval Process](#approval-process)
7. [Advanced Configuration](#advanced-configuration)
8. [Troubleshooting](#troubleshooting)

---

## Installation

### Step 1: Install the Module
1. Go to **Apps** menu
2. Remove the **Apps** filter to see all modules
3. Search for **"Advanced Approval Workflow"**
4. Click **Install**

### Step 2: Verify Installation
1. After installation, you should see a new menu **"Approvals"** in the main menu
2. The menu should contain:
   - **Requests** (visible to all approval users)
   - **Types** (visible only to approval managers)

---

## User Groups Setup

### Step 1: Assign Users to Groups
1. Go to **Settings** → **Users & Companies** → **Users**
2. Select a user you want to give approval access
3. Click **Edit**
4. Go to the **Access Rights** tab
5. Find and check:
   - **Approval User** - For regular users who can create and approve requests
   - **Approval Manager** - For managers who can configure approval types and manage all requests

### Step 2: Group Permissions Summary
- **Approval User**: Can create, view, and approve requests assigned to them
- **Approval Manager**: All user permissions + can create/edit approval types and change approvers

---

## Creating Approval Types

### Step 1: Access Approval Types
1. Go to **Approvals** → **Types** (only visible to Approval Managers)
2. Click **Create**

### Step 2: Basic Configuration
1. **Name**: Enter a descriptive name (e.g., "Purchase Order Approval", "Product Price Change")
2. **Sequence**: Set the order for display (lower numbers appear first)
3. **Active**: Keep checked to enable this approval type
4. **Company**: Select company if using multi-company setup

### Step 3: Configure Approval Lines (Approvers)
1. In the **Approval Lines** tab, click **Add a line**
2. For each approver level:
   - **Sequence**: Order of approval (1 = first approver, 2 = second, etc.)
   - **Name**: Description of this approval level (e.g., "Department Manager", "Finance Director")
   - **User**: Select the specific user who will approve
   - **Required/Optional**: 
     - **Required**: Must be approved to proceed
     - **Optional**: Can be skipped if not available

3. **Example Multi-Level Setup**:
   ```
   Sequence 1: Department Manager (Required)
   Sequence 2: Finance Director (Required)
   Sequence 3: CEO (Optional)
   ```

### Step 4: Advanced Configuration (Optional)
1. Go to **Model Configuration** tab
2. **Apply for Model**: Check if you want automatic approval for specific models
3. **Target Model**: Select the model (e.g., Product Template, Sale Order)
4. **Activation Domain**: Set conditions when approval is required
   - Example: `[('list_price', '>', 1000)]` - Requires approval if price > 1000

### Step 5: Save
Click **Save** to create the approval type

---

## Configuring Approval Lines

### Step 1: Understanding Approval Flow
- Approvals work **sequentially** (one after another)
- First approver (sequence 1) must approve before second approver can see it
- All **Required** approvers must approve
- **Optional** approvers can be skipped

### Step 2: Special User Options (HR Module Required)
If you have HR module installed, you can use:
- **Manager**: Automatically uses the requester's manager
- **Department Manager**: Automatically uses the department manager

### Step 3: Best Practices
- Start with sequence 1 for the first approver
- Use clear names for each level
- Mark critical approvers as **Required**
- Use **Optional** for advisory approvals

---

## Creating Approval Requests

### Step 1: Create New Request
1. Go to **Approvals** → **Requests**
2. Click **Create**

### Step 2: Fill Request Details
1. **Name**: Enter a descriptive name for the request
   - Example: "Approve new product pricing for Product XYZ"
2. **Type**: Select the approval type you configured
3. **Source Document** (Optional): Link to the related document
   - Can link to Products, Sale Orders, Purchase Orders, etc.

### Step 3: Submit for Approval
1. Click **Save**
2. Click **Submit** button
3. The system will:
   - Create approval lines based on the approval type
   - Assign the first approver
   - Send notification to the first approver
   - Change status to **Submitted**

---

## Approval Process

### For Approvers:

#### Step 1: View Pending Approvals
1. Go to **Approvals** → **Requests**
2. Use filter **"My Approvals"** to see requests waiting for your approval
3. Or filter by **"Submitted"** status

#### Step 2: Review Request
1. Open the approval request
2. Review all details including:
   - Request information
   - Approval lines (who needs to approve)
   - Source document (if linked)
   - Comments/Notes

#### Step 3: Approve or Refuse
**To Approve:**
1. Click **Approve** button
2. The system will:
   - Mark your approval as complete
   - Move to next approver (if any)
   - Send notification to next approver
   - If you're the last approver, mark request as **Approved**

**To Refuse:**
1. Click **Refuse** button
2. Enter the refusal reason
3. Click **Refuse**
4. The system will:
   - Mark request as **Refused**
   - Notify the requester
   - Stop the approval process

### For Requesters:

#### Step 1: Track Your Requests
1. Go to **Approvals** → **Requests**
2. Use filter **"My Requests"** to see all your requests
3. Check status:
   - **Draft**: Not yet submitted
   - **Submitted**: Waiting for approval
   - **Approved**: All approvals received
   - **Refused**: Rejected by an approver
   - **Cancelled**: Cancelled by user

#### Step 2: Rework Refused Requests (Optional)
1. If a request is refused, you can rework it:
   - Go to the refused request
   - Click **Action** → **Rework Approval**
   - Enter rework reason
   - Request will return to **Draft** status
   - You can modify and resubmit

#### Step 3: Cancel Requests (Optional)
1. If you need to cancel a request:
   - Go to the request
   - Click **Action** → **Cancel Approval**
   - Enter cancellation reason (optional)
   - Request will be marked as **Cancelled**

---

## Advanced Configuration

### Model-Based Automatic Approval

#### Step 1: Enable Model Configuration
1. Go to **Approvals** → **Types**
2. Select or create an approval type
3. Go to **Model Configuration** tab
4. Check **Apply for Model**

#### Step 2: Configure Target Model
1. **Target Model**: Select the model that needs approval
   - Example: Product Template, Sale Order
2. **Activation Domain**: Set conditions
   - Example: `[('list_price', '>', 1000)]`
   - This means: Approval required when price > 1000

#### Step 3: Technical Fields
The system automatically creates these fields on the target model:
- `x_need_approval`: Boolean - Indicates if approval is needed
- `x_has_request_approval`: Boolean - Indicates if request exists
- `x_review_result`: Char - Stores approval result (approved/refused)

#### Step 4: Using Model-Based Approval
1. When creating/editing a record that matches the domain:
   - The system will require approval before saving
   - Use the **Request Approval** wizard to create approval request
   - Once approved, the record can be modified

### Changing Approvers (Managers Only)

#### Step 1: Access Change Approver
1. Go to **Approvals** → **Requests**
2. Open a submitted request
3. Click **Action** → **Change Approver**

#### Step 2: Select New Approver
1. Select the approval line to change
2. Select the new approver
3. Click **Change**

---

## Troubleshooting

### Issue: "No approvers configured"
**Solution**: 
- Go to the Approval Type
- Add at least one approval line in the Approval Lines tab

### Issue: "Not authorized" when trying to approve
**Solution**:
- Check if you're assigned as the approver for that level
- Only the current approver (sequence) can approve

### Issue: Can't see "Types" menu
**Solution**:
- You need **Approval Manager** group access
- Go to Settings → Users → Your User → Access Rights → Check "Approval Manager"

### Issue: Approval stuck in "Submitted" status
**Solution**:
- Check if all required approvers have approved
- Verify the approval lines are correctly configured
- Check if there are any optional approvers that can be skipped

### Issue: Can't create approval request
**Solution**:
- Verify you have **Approval User** group access
- Check that the approval type is active
- Ensure the approval type has at least one approval line

### Issue: Model-based approval not working
**Solution**:
- Verify the domain syntax is correct (use Odoo domain format)
- Check that the target model is selected
- Ensure "Apply for Model" is checked
- The technical fields are created automatically on first use

---

## Quick Reference

### Approval States
- **Draft**: Request created but not submitted
- **Submitted**: Waiting for approval
- **Approved**: All approvals received
- **Refused**: Rejected by an approver
- **Cancelled**: Cancelled by user

### User Roles
- **Approval User**: Create and approve requests
- **Approval Manager**: Full access including configuration

### Key Features
- Multi-level sequential approvals
- Required/Optional approvers
- Model-based automatic approval
- Email notifications
- Rework and cancel options
- Manager-based approver assignment (with HR module)

---

## Example Workflow

### Scenario: Product Price Change Approval

1. **Create Approval Type**:
   - Name: "Product Price Change Approval"
   - Add Approval Lines:
     - Sequence 1: Sales Manager (Required)
     - Sequence 2: Finance Director (Required)
     - Sequence 3: CEO (Optional)

2. **Create Request**:
   - Name: "Approve price change for Product ABC"
   - Type: Product Price Change Approval
   - Source Document: Link to the product

3. **Submit**: Request goes to Sales Manager

4. **Sales Manager Approves**: Request moves to Finance Director

5. **Finance Director Approves**: Request is fully approved

6. **Result**: Product can be updated with new price

---

**End of Configuration Guide**

