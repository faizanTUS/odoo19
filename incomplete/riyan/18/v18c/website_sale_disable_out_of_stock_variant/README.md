# Website Disable Out of Stock Product Variant

Odoo 18 module that automatically disables out-of-stock product variants on the website with a single setting. Keeps the storefront clear and prevents customers from selecting unavailable items.

## Features

- **Single setting**: Enable/disable from **Settings → Website** (Shop - Products).
- **Product page**: Out-of-stock variants show *"This combination does not exist."* and the **Add to cart** button is disabled.
- **Product stays visible**: Only the unavailable variant is disabled; the product page remains visible.
- **Stock-based**: Uses inventory (Product Availability / `website_sale_stock`); non-storable products are unaffected.
- **Hide from shop (optional)**: Enable **Hide Out of Stock Products from Shop** so products with 0 on hand (e.g. Corner Desk Right Sit) do not appear in the shop listing at all—only in-stock or non-storable products are shown.

## Requirements

- **Odoo 18**
- **website_sale**
- **website_sale_stock** (Product Availability)

## Installation

1. Copy the module folder `website_sale_disable_out_of_stock_variant` into your addons path (e.g. `project/` or `addons/`).
2. Update the Apps list: **Apps** → **Update Apps List**.
3. Search for **Website Disable Out of Stock Product Variant** and click **Install**.

## Step-by-Step Configuration

### 1. Enable the feature

1. Go to **Settings** (gear icon).
2. In the left menu, open **Website**.
3. Scroll to the **Shop - Products** block.
4. Find **Disable Out of Stock Product Variant**.
5. Check the box: **Disable out of stock product variant for add to cart**.
6. Click **Save**.

**Path:** Settings → Website → Shop - Products → **Disable Out of Stock Product Variant** (checkbox).

### 1b. (Optional) Hide out-of-stock products from the shop listing

If you want products with **0 on hand** (like Corner Desk Right Sit) to **not appear at all** on the shop page (/shop):

1. In **Settings** → **Website** → **Shop - Products**, enable **Hide Out of Stock Products from Shop**.
2. Click **Save**.

Products with no available quantity will be hidden from the shop grid; only products with at least one variant in stock (or non-storable products) are shown.

### 2. Ensure products use stock

1. Go to **Inventory** (or **Sales** → Products).
2. Open a product that has **variants** (e.g. LEGS, COLOR).
3. In the **Inventory** tab, ensure **Storable Product** is set and **On Hand** is updated (e.g. **0.00 Units** for an out-of-stock variant).
4. Publish the product on the website if needed (**Sales** tab → **eCommerce**).

### 3. Check behaviour on the shop

1. Open your **Website** → **Shop**.
2. Open a product that has at least one **out-of-stock** variant (On Hand = 0).
3. Select the combination that is out of stock (e.g. LEGS: Aluminium, COLOR: Black).
4. You should see:
   - Message: **"This combination does not exist."**
   - **Add to cart** button **disabled** (greyed out).
5. Select a variant that is in stock: **Add to cart** should be enabled and work as usual.

## How it works

- When **Disable Out of Stock Product Variant** is enabled:
  - For each variant, the system checks **free quantity** (website warehouse).
  - If **free_qty ≤ 0** for a storable variant:
    - That variant is treated as an impossible combination: *"This combination does not exist."* is shown and Add to cart is disabled.
    - Adding that variant to cart via other means (e.g. direct link) is still blocked by `_is_add_to_cart_allowed`.
- Non-storable products and variants with stock are unchanged.

## Disabling the feature

1. **Settings** → **Website** → **Shop - Products**.
2. Uncheck **Disable Out of Stock Product Variant**.
3. **Save**.

Out-of-stock variants will again follow the default behaviour (e.g. **Continue selling when out-of-stock** in **Inventory Defaults**).

## License

LGPL-3.
