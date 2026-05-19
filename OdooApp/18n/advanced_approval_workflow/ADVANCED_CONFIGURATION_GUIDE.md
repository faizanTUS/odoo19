# Advanced Configuration - Model-Based Approval Setup Guide

## Overview
This guide explains how to configure automatic approval requirements for specific Odoo models based on domain conditions. This feature allows you to automatically require approval when certain conditions are met (e.g., product price > $1000).

---

## Prerequisites
- You must have **Approval Manager** access rights
- The approval type must already be created
- You need to understand Odoo domain syntax

---

## Step-by-Step Configuration

### Step 1: Access the Approval Type
1. Log in as a user with **Approval Manager** rights
2. Navigate to **Approvals** → **Types**
3. Either:
   - **Create a new approval type**, OR
   - **Edit an existing approval type** (click on it to open)

### Step 2: Complete Basic Configuration
Before setting up model-based approval, ensure you have:
1. **Name**: Enter a descriptive name (e.g., "Product Price Approval")
2. **Approval Lines**: Configure at least one approver (see main configuration guide)
3. Click **Save** to save basic settings

### Step 3: Navigate to Model Configuration Tab
1. In the approval type form, you'll see a notebook with tabs at the bottom
2. Click on the **"Model Configuration"** tab
   - **Note**: This tab is only visible to Approval Managers
   - The tab will appear after you check "Apply for Model"

### Step 4: Enable Model-Based Approval
1. In the **Model Configuration** tab, locate the **"Apply for Model"** checkbox
2. **Check the box** to enable model-based approval
3. Once checked, the other fields in this section will become visible and required

### Step 5: Select Target Model
1. Click on the **"Target Model"** dropdown field
2. You'll see a list of available models:
   - **Product Product** (`product.product`) - Individual products
   - **Product Template** (`product.template`) - Product templates
   - **Sale Order** (`sale.order`) - Sales orders
   - **Purchase Order** (`purchase.order`) - Purchase orders
   - **Account Move** (`account.move`) - Invoices/Bills
   - **Stock Picking** (`stock.picking`) - Stock transfers

3. **Select the model** you want to protect with approval
   - Example: Select **"Product Template"** if you want to require approval for product price changes

### Step 6: Configure Activation Domain
This is the most important step. The domain determines **when** approval is required.

#### Understanding Domain Syntax
Domains in Odoo use Python list syntax with tuples:
```python
[('field_name', 'operator', 'value')]
```

#### Common Operators:
- `=` : Equal to
- `!=` : Not equal to
- `>` : Greater than
- `>=` : Greater than or equal to
- `<` : Less than
- `<=` : Less than or equal to
- `in` : Value is in list
- `not in` : Value is not in list
- `like` : Text contains (case-sensitive)
- `ilike` : Text contains (case-insensitive)

#### Domain Examples by Model:

##### Example 1: Product Template - Price-Based Approval
**Scenario**: Require approval when product price exceeds $1000

1. **Target Model**: Select "Product Template"
2. **Activation Domain**: Enter the following:
   ```python
   [('list_price', '>', 1000)]
   ```
3. **Explanation**:
   - `list_price` is the field name for product price
   - `>` means greater than
   - `1000` is the threshold value

##### Example 2: Product Template - Multiple Conditions
**Scenario**: Require approval for products with price > $500 AND category is "Electronics"

1. **Target Model**: Select "Product Template"
2. **Activation Domain**: Enter:
   ```python
   [('list_price', '>', 500), ('categ_id.name', '=', 'Electronics')]
   ```
3. **Explanation**:
   - Multiple conditions are separated by commas
   - All conditions must be true (AND logic)
   - `categ_id.name` accesses the category name through the Many2one relationship

##### Example 3: Sale Order - Amount-Based Approval
**Scenario**: Require approval for sales orders with total amount > $10,000

1. **Target Model**: Select "Sale Order"
2. **Activation Domain**: Enter:
   ```python
   [('amount_total', '>', 10000)]
   ```
3. **Explanation**:
   - `amount_total` is the total amount field
   - Approval required when order value exceeds $10,000

##### Example 4: Sale Order - Customer Credit Limit
**Scenario**: Require approval when customer credit limit is exceeded

1. **Target Model**: Select "Sale Order"
2. **Activation Domain**: Enter:
   ```python
   [('amount_total', '>', 'partner_id.credit_limit')]
   ```
   **Note**: This requires the credit_limit field to exist on the partner

##### Example 5: Purchase Order - Department-Based
**Scenario**: Require approval for purchase orders from specific departments

1. **Target Model**: Select "Purchase Order"
2. **Activation Domain**: Enter:
   ```python
   [('department_id.name', 'in', ['IT', 'Finance', 'Operations'])]
   ```
3. **Explanation**:
   - `in` operator checks if value is in the list
   - Approval required for orders from IT, Finance, or Operations departments

##### Example 6: Product Template - Status and Price
**Scenario**: Require approval for active products with price > $2000

1. **Target Model**: Select "Product Template"
2. **Activation Domain**: Enter:
   ```python
   [('active', '=', True), ('list_price', '>', 2000)]
   ```
3. **Explanation**:
   - `active` field checks if product is active
   - Both conditions must be true

##### Example 7: Using OR Logic
**Scenario**: Require approval if price > $1000 OR category is "Premium"

1. **Target Model**: Select "Product Template"
2. **Activation Domain**: Enter:
   ```python
   ['|', ('list_price', '>', 1000), ('categ_id.name', '=', 'Premium')]
   ```
3. **Explanation**:
   - `'|'` (pipe symbol) means OR
   - The pipe applies to the next two conditions
   - Approval required if EITHER condition is true

##### Example 8: Complex OR and AND Combination
**Scenario**: Require approval if (price > $1000 AND active) OR category is "Premium"

1. **Target Model**: Select "Product Template"
2. **Activation Domain**: Enter:
   ```python
   ['|', '&', ('list_price', '>', 1000), ('active', '=', True), ('categ_id.name', '=', 'Premium')]
   ```
3. **Explanation**:
   - `'&'` means AND
   - `'|'` means OR
   - Operators apply to following conditions
   - Structure: OR(AND(price>1000, active), category='Premium')

### Step 7: Save Configuration
1. After entering the domain, click **Save**
2. The system will:
   - Validate the domain syntax
   - Create technical fields on the target model (if not already created)
   - Enable write protection for matching records

### Step 8: Verify Technical Fields Created
After saving, the system automatically creates these fields on the target model:
- `x_need_approval` (Boolean): Indicates if approval is needed
- `x_has_request_approval` (Boolean): Indicates if approval request exists
- `x_review_result` (Char): Stores approval result (approved/refused)

**Note**: These fields are created automatically and are read-only for users.

---

## How It Works in Practice

### Scenario: Product Price Approval

#### Setup:
1. Approval Type: "Product Price Approval"
2. Target Model: Product Template
3. Domain: `[('list_price', '>', 1000)]`
4. Approvers: Sales Manager → Finance Director

#### User Workflow:

**Step 1: User Tries to Change Price**
1. User opens a product
2. Changes price from $800 to $1200
3. Tries to save

**Step 2: System Checks Domain**
1. System evaluates: Is `list_price > 1000`? Yes (1200 > 1000)
2. Domain matches, so approval is required

**Step 3: Create Approval Request**
1. User must create an approval request before saving
2. Go to the product form
3. Use "Request Approval" action/wizard (if available)
4. Or manually create request in Approvals → Requests
5. Link the request to the product

**Step 4: Approval Process**
1. Request goes through configured approvers
2. Once approved, the product can be saved with new price
3. The `x_review_result` field is set to "approved"

**Step 5: Save Product**
1. After approval, user can save the product
2. The write protection is bypassed using `approval_bypass` context

---

## Domain Syntax Reference

### Basic Structure
```python
[('field_name', 'operator', 'value')]
```

### Field Types and Examples

#### Text Fields
```python
[('name', '=', 'Product Name')]
[('name', 'ilike', 'laptop')]  # Case-insensitive search
[('name', 'like', 'Laptop%')]  # Starts with "Laptop"
```

#### Numeric Fields
```python
[('list_price', '>', 1000)]
[('qty_available', '>=', 50)]
[('weight', '<', 10.5)]
```

#### Boolean Fields
```python
[('active', '=', True)]
[('sale_ok', '=', False)]
```

#### Date Fields
```python
[('date_created', '>', '2024-01-01')]
[('expiry_date', '<', '2024-12-31')]
```

#### Many2one Fields (Related Fields)
```python
[('categ_id.name', '=', 'Electronics')]  # Category name
[('partner_id.country_id.code', '=', 'US')]  # Partner's country code
[('user_id.id', '=', 5)]  # Specific user ID
```

#### Selection Fields
```python
[('state', 'in', ['draft', 'sent'])]
[('priority', '=', 'high')]
```

### Logical Operators

#### AND (default - no operator needed)
```python
[('field1', '>', 100), ('field2', '=', 'value')]
# Both conditions must be true
```

#### OR (use '|')
```python
['|', ('field1', '>', 100), ('field2', '=', 'value')]
# Either condition can be true
```

#### NOT (use '!')
```python
['!', ('field1', '=', 'value')]
# Condition must be false
```

#### Complex Combinations
```python
# (A AND B) OR C
['|', '&', ('A', '=', 1), ('B', '=', 2), ('C', '=', 3)]

# A OR (B AND C)
['|', ('A', '=', 1), '&', ('B', '=', 2), ('C', '=', 3)]
```

---

## Common Field Names by Model

### Product Template (`product.template`)
- `list_price` - Sale price
- `standard_price` - Cost price
- `qty_available` - Available quantity
- `categ_id` - Product category
- `active` - Active status
- `type` - Product type (consu, service, product)

### Sale Order (`sale.order`)
- `amount_total` - Total amount
- `amount_untaxed` - Untaxed amount
- `partner_id` - Customer
- `user_id` - Salesperson
- `state` - Order state
- `date_order` - Order date

### Purchase Order (`purchase.order`)
- `amount_total` - Total amount
- `partner_id` - Vendor
- `state` - Order state
- `date_order` - Order date

### Account Move (`account.move`)
- `amount_total` - Total amount
- `partner_id` - Partner
- `move_type` - Move type (invoice, entry, etc.)
- `state` - Invoice state

---

## Testing Your Configuration

### Step 1: Create Test Record
1. Create or edit a record that matches your domain
2. Example: Create a product with price > $1000

### Step 2: Verify Write Protection
1. Try to save the record
2. You should see an error: "This document requires approval before modification"
3. This confirms the protection is working

### Step 3: Create Approval Request
1. Create an approval request for the record
2. Link it to the record using "Source Document" field
3. Submit for approval

### Step 4: Complete Approval
1. Have approvers approve the request
2. After approval, try saving the record again
3. It should save successfully

---

## Troubleshooting

### Issue: Domain Syntax Error
**Error**: "Invalid domain syntax"
**Solution**:
- Check for proper Python list syntax: `[...]`
- Ensure tuples use parentheses: `('field', 'operator', 'value')`
- Check for matching brackets and quotes
- Use single quotes for strings: `'value'` not `"value"`

### Issue: Field Not Found
**Error**: "Field 'xxx' does not exist"
**Solution**:
- Verify the field name is correct
- Check field name in model (Settings → Technical → Database Structure → Models)
- For related fields, use dot notation: `partner_id.name`

### Issue: Domain Not Working
**Problem**: Approval not required when it should be
**Solution**:
- Verify domain syntax is correct
- Test domain manually: Go to the model list view, add the domain as a filter
- Check if field values actually match the domain
- Ensure "Apply for Model" is checked and saved

### Issue: Can't Save After Approval
**Problem**: Still can't save even after approval
**Solution**:
- Verify approval request is linked to the record (origin_ref field)
- Check that approval request status is "Approved"
- Ensure the `run()` method is executing properly
- Check if `x_review_result` field is set to "approved"

### Issue: Technical Fields Not Created
**Problem**: Fields x_need_approval, etc. not appearing
**Solution**:
- Save the approval type after configuring model
- Check if you have system administrator rights
- Verify the model_id is correctly selected
- Check Odoo logs for errors

---

## Best Practices

1. **Start Simple**: Begin with simple domains, then add complexity
2. **Test Thoroughly**: Always test with sample data before deploying
3. **Document Domains**: Keep notes on what each domain does
4. **Use Clear Names**: Name approval types descriptively
5. **Review Regularly**: Periodically review if domains still match business needs
6. **Backup First**: Test in a development environment first

---

## Advanced Examples

### Example: Multi-Condition Product Approval
```python
# Require approval for:
# - Products with price > $1000 AND
# - Category is "Electronics" OR "Computers" AND
# - Product is active
['&', '&', ('list_price', '>', 1000), 
     '|', ('categ_id.name', '=', 'Electronics'), 
          ('categ_id.name', '=', 'Computers'),
     ('active', '=', True)]
```

### Example: Sale Order by Amount and Customer
```python
# Require approval for:
# - Orders with amount > $5000 OR
# - Orders from customers in specific countries
['|', ('amount_total', '>', 5000),
     ('partner_id.country_id.code', 'in', ['US', 'CA', 'MX'])]
```

### Example: Date-Based Approval
```python
# Require approval for orders created after a certain date
[('date_order', '>', '2024-01-01')]
```

---

## Summary

Model-based approval allows you to:
- ✅ Automatically require approval based on record conditions
- ✅ Protect critical data changes
- ✅ Enforce business rules through approval workflows
- ✅ Track approval status on records

**Key Points to Remember**:
1. Only Approval Managers can configure this
2. Domain syntax must be valid Python list format
3. Technical fields are created automatically
4. Records matching domain require approval before saving
5. Approval must be completed before record can be saved

---

**End of Advanced Configuration Guide**

