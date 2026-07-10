# Step-by-Step Configuration: Centralized Pricelist & Vendor Pricing Setup | Sales & Purchase Pricing

This guide walks you through configuring **Sale Pricelists** and **Vendor (Partner) Price Rules** in Odoo, including
**Import Excel with Options** and **Product Matching Options** for pricelist lines, and how to use the sample import files shipped with this module.

---

## Part 1: Sale Pricelist Configuration

### 1.1 Where to find Sale Pricelists

- **Sales** → **Products** → **Pricelists**  
- **Sales** → **Configuration** → **Pricelist & Vendor Setup** → **Sale Pricelists**

### 1.2 Basic steps to create and import a pricelist

1. Go to **Sales** → **Products** → **Pricelists** 
2. Click **New** (Create).
3. Fill in:
   - **Pricelist Name**: e.g. `Public Pricelist`, `Wholesale`, `Retail`.
   - **Currency**: e.g. USD, EUR.
   - **Company**: leave default or select.
4. Open the **Price Rules** tab.
5. **Apply On** (for rules): choose **Product**, **Product Variant**, **Product Category**, or **All Products**.
6. Add rules either:
   - **Add a line** – add one rule at a time (Product/Variant, Min. Quantity, Price, Start Date, End Date, Discount (%)).
   - **Import Pricelist Line** / **Import records** – bulk import from Excel/CSV (see section 1.4 below).
7. Save.

### 1.3 Add a Pricelist Item from the Product form

1. Go to **Sales** → **Products** → **Products** and open a product.
2. Open the **Sales** tab.
3. In the **Pricelists** section, click **Add a line**.
4. In the popup:
   - **Pricelist**: e.g. Public Pricelist.
   - **Product** / **Variant**: pre-filled from the product.
   - **Min. Quantity**: e.g. `1.00`.
   - **Compute Price**: **Fixed Price** (or Discount/Formula).
   - **Fixed Price**: e.g. `10.00`.
   - **Start Date** / **End Date**: optional.
5. Save. The new line appears in the product’s Pricelists table.

### 1.4 Import Pricelist Lines with Excel (Import with Options)

Use this when you want to bulk import pricelist items (price rules) from an Excel or CSV file. The **Product Matching Options** setting tells Odoo how to match your file columns to products and variants.

#### Open the import dialog

1. Go to **Sales** → **Configuration** → **Pricelist & Vendor Setup** → **Sale Pricelist Rules** (or open a pricelist and use the **Price Rules** tab, then **Import records** from the list view).
2. Click **Favorites** (⋮) → **Import records**.
3. Upload your Excel or CSV file.

#### Import options

- **Use First Row as Header**: Leave checked if the first row contains column names (Product, Variant, Min. Qty, Price, etc.).
- **Create new records**: Check to create new pricelist items.
- **Update existing records**: Check to update existing items (e.g. when re-importing with the same product/variant and pricelist).
- **Date Format** / **Number Format**: Set to match your file (e.g. `%Y-%m-%d` for dates).

#### Product Matching Options (important)

Choose how Odoo matches rows to products and variants:

| Option | Use when | Your file must include |
|--------|----------|------------------------|
| **Product by Name & Product Variants by Internal Reference / Code** | Variants are identified by **Internal Reference** (default code) | Column **Product** (template name) and **Variant** (internal reference/code). |
| **Product by Name & Product Variants by Barcode** | Variants are identified by **Barcode** | Column **Product** (template name) and **Barcode**. |

Map your Excel columns to Odoo fields, for example:

- **Product Name** ← Product (template name)
- **Product Variant Name** (or **Variant**) ← Variant internal reference when using “by Code”; or use **Barcode** when using “by Barcode”
- **Min. Quantity** ← Min. Qty
- **Price** ← Price (fixed price)
- **Start Date** / **End Date** ← Validity
- **Discount (%)** ← Discount

Then click **Test Import** to validate, then **Import**.

#### Sample files for the two scenarios

- **Scenario 1 – Product by Name & Variants by Internal Reference / Code**  
  Use **sample_pricelist_items_by_name_and_variant_code.csv**.  
  Columns: `Product`, `Variant` (internal reference), `Min. Qty`, `Price`, `Start Date`, `End Date`, `Discount (%)`.

- **Scenario 2 – Product by Name & Product Variants by Barcode**  
  Use **sample_pricelist_items_by_name_and_barcode.csv**.  
  Columns: `Product`, `Barcode`, `Min. Qty`, `Price`, `Start Date`, `End Date`, `Discount (%)`.

Ensure products and variants exist in Odoo and that **Variant** (internal reference) or **Barcode** values in the file match exactly.

### 1.5 Import a Sale Pricelist (header only)

1. Go to **Sales** → **Products** → **Pricelists**.
2. Click **Favorites** (⋮) → **Import records** (or use the import option from the list view).
3. Upload a file with columns such as:
   - `name` → Pricelist Name  
   - `currency_id/name` or `currency_id` → Currency (e.g. USD)
4. Map columns to Odoo fields, then **Test** and **Import**.

### 1.6 Import Sale Pricelist Rules (full field mapping, product.pricelist.item)

1. Go to **Sales** → **Configuration** → **Pricelist & Vendor Setup** → **Sale Pricelist Rules** (or **Sales** → **Products** → **Pricelists** and use the **Price Rules** action if available).
2. In the list view, click **Favorites** (⋮) → **Import records**.
3. Use the sample file **sample_sale_pricelist_rules.csv** from this module’s `data/` folder (or the scenario-based files in section 1.4).  
   Key columns:
   - `pricelist_id/name` – Pricelist name (must exist).
   - `product_tmpl_id/name` – Product name (template).
   - `product_id/name` – Variant name (optional).
   - `min_quantity` – Min. quantity.
   - `fixed_price` – Price (when using Fixed Price).
   - `compute_price` – `fixed` | `percentage` | `formula`.
   - `applied_on` – `3_global` | `2_product_category` | `1_product` | `0_product_variant`.
   - `date_start`, `date_end` – Validity (optional).

---

## Part 2: Vendor (Partner Price Rules) Configuration

Vendor prices in Odoo are stored in **Vendor Pricelists** (model: **product.supplierinfo**). They define **per-product, per-vendor** prices, min quantity, lead time, and validity.

### 2.1 Where to find Vendor Pricelists

- **Purchase** → **Configuration** → **Vendor Pricelists**  
  or  
- **Sales** → **Configuration** → **Pricelist & Vendor Setup** → **Vendor Price Rules**  
  or from a product: **Purchase** tab → **Vendors** section.

### 2.2 Add a vendor from the Product form

1. Go to **Sales** → **Products** → **Products** and open a product.
2. Open the **Purchase** tab.
3. In the **Vendors** section, click **Add a line**.
4. In the popup:
   - **Vendor**: select contact (must be a **Vendor**).
   - **Quantity**: min quantity for this price (e.g. 1).
   - **Unit of Measure**: usually default.
   - **Price**: e.g. `5.00`.
   - **Delivery Lead Time**: days (e.g. 1).
   - **Validity**: Start/End dates (optional).
5. Save. The line appears in the product’s Vendors table.

### 2.3 Create / edit Vendor Price Rules from the list

1. Go to **Purchase** → **Configuration** → **Vendor Pricelists** (or **Pricelist & Vendor Setup** → **Vendor Price Rules**).
2. You see a list: **Product**, **Supplier**, **Price**, **Min. Quantity**, **Validity Start Date**, **Validity End Date**.
3. Click **New** to create a rule:
   - **Product** / **Product Variant**: choose product (template) or variant.
   - **Vendor**: choose supplier.
   - **Min Quantity**: e.g. 1.
   - **Price**: e.g. 10.00.
   - **Start Date** / **End Date**: validity (optional).
   - **Company**, **Currency**, **Delay** (lead time in days) as needed.
4. Save.

### 2.4 Import Vendor Price Rules (product.supplierinfo)

1. Go to **Purchase** → **Configuration** → **Vendor Pricelists**.
2. Use **Favorites** (⋮) → **Import records** (or the list’s Import option).
3. Use the sample file **sample_vendor_price_rules.csv** from this module’s `data/` folder.  
   Key columns:
   - `product_tmpl_id/name` – Product (template) name.
   - `product_id/name` – Variant name (optional).
   - `partner_id/name` – Vendor/Supplier name.
   - `min_qty` – Min. quantity.
   - `price` – Unit price.
   - `date_start`, `date_end` – Validity (optional).
   - `delay` – Delivery lead time (days).
   - `product_code`, `product_name` – Vendor product code/name (optional).

---

## Part 3: Product import (with optional references for Pricelist & Vendor)

Products are imported separately. Pricelist items and vendor lines are linked by **product name** (or internal reference) when you import **product.pricelist.item** and **product.supplierinfo**; product names in those files must match existing product names (or you import products first).

### 3.1 Product import file columns (product.template)

Use **sample_products.csv** as a reference. Typical columns:

- `name` – Product Name  
- `list_price` – Sales Price  
- `standard_price` – Cost  
- `type` – Product Type: `consu` (Goods), `service`, `combo`  
- `categ_id/name` – Category (e.g. `All / Saleable`)  
- `default_code` – Internal Reference  
- `barcode` – Barcode  
- `uom_id/name` – Sales UoM (e.g. Units)  
- `uom_po_id/name` – Purchase UoM  
- `taxes_id/name` – Customer taxes (optional)  
- `supplier_taxes_id/name` – Vendor taxes (optional)  
- `weight`, `volume` – Optional  

Pricelist and vendor data are **not** in the product import; use the dedicated pricelist and vendor CSV files above.

---

## Part 4: Sample import files (this module)

Location (relative to your addons path):

`odoo_pricelist_import/data/`

| File | Model | Purpose |
|------|--------|--------|
| `sample_sale_pricelist.csv` | product.pricelist | Create pricelists (name, currency). |
| `sample_sale_pricelist_rules.csv` | product.pricelist.item | Create sale pricelist rules (product, min qty, price, dates) – full field names. |
| `sample_pricelist_items_by_name_and_variant_code.csv` | product.pricelist.item | Import pricelist lines with **Product by Name & Variants by Internal Reference / Code**. |
| `sample_pricelist_items_by_name_and_barcode.csv` | product.pricelist.item | Import pricelist lines with **Product by Name & Product Variants by Barcode**. |
| `sample_vendor_price_rules.csv` | product.supplierinfo | Create vendor price rules (product, vendor, min qty, price, dates, delay). |
| `sample_products.csv` | product.template | Create/update products (name, price, cost, category, internal reference, barcode). |

### Import order suggestion

1. **Products** – Import **sample_products.csv** (or your own) so products and variants exist (with Internal Reference and/or Barcode if you use the scenario-based pricelist imports).
2. **Sale Pricelists** – Import **sample_sale_pricelist.csv** so pricelists exist.
3. **Sale Pricelist Rules** – Use **sample_sale_pricelist_rules.csv** (full field names), or **sample_pricelist_items_by_name_and_variant_code.csv** / **sample_pricelist_items_by_name_and_barcode.csv** with the matching **Product Matching Options** in the import dialog.
4. **Vendor Price Rules** – Import **sample_vendor_price_rules.csv** (reference product name and vendor name).

Ensure **Vendors** (Contacts with “Vendor” checked) and **Pricelists** exist before importing rules that reference them.

---

## Part 5: Field mapping reference

### Sale Pricelist (product.pricelist)

| Odoo field | Description | Import column example |
|------------|-------------|------------------------|
| name | Pricelist Name | name |
| currency_id | Currency | currency_id/name (e.g. USD) |
| company_id | Company | company_id/name (optional) |

### Sale Pricelist Rule (product.pricelist.item)

| Odoo field | Description | Import column example |
|------------|-------------|------------------------|
| pricelist_id | Pricelist | pricelist_id/name |
| product_tmpl_id | Product (template) | product_tmpl_id/name |
| product_id | Variant | product_id/name (optional) |
| min_quantity | Min. Quantity | min_quantity |
| fixed_price | Fixed Price | fixed_price |
| compute_price | fixed / percentage / formula | compute_price |
| applied_on | 3_global / 1_product / 0_product_variant / 2_product_category | applied_on |
| date_start | Start Date | date_start |
| date_end | End Date | date_end |
| base | list_price / standard_price / pricelist | base (optional) |

### Vendor Price Rule (product.supplierinfo)

| Odoo field | Description | Import column example |
|------------|-------------|------------------------|
| product_tmpl_id | Product (template) | product_tmpl_id/name |
| product_id | Variant | product_id/name (optional) |
| partner_id | Vendor | partner_id/name |
| min_qty | Min. Quantity | min_qty |
| price | Price | price |
| date_start | Start Date | date_start |
| date_end | End Date | date_end |
| delay | Delivery Lead Time (days) | delay |
| product_code | Vendor Product Code | product_code |
| product_name | Vendor Product Name | product_name |

---

## Troubleshooting

- **“You cannot create a record while a wizard is running”**  
  Close any open wizard (e.g. import or configuration) and try again.

- **Invalid Product / Pricelist / Vendor**  
  Ensure names in the CSV exactly match existing records (or create them first). Use Internal Reference or exact name.

- **Date format**  
  Use the format expected by Odoo (e.g. `%Y-%m-%d` or as set in the import wizard). In the samples we use `YYYY-MM-DD`.

- **Vendor not found**  
  The contact must have **Vendors** checked (Purchase → Vendors or Contact form → Purchase tab).

For more details, see the standard Odoo documentation on **Import** and **Pricelists**.
