/** @odoo-module **/
import { Component, useState ,onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";


const actionRegistry = registry.category("actions");

export class BulkOrderGridComponent extends Component {
    static template = "tus_add_bulk_order.BulkOrderGridComponent";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.actionService = useService("action");
        this.saleOrderId = this.props.action.context?.active_id || null;
        this.saleOrderName = ''
        this.copiedQuantities = null; // Will store an array of variant quantities

        this.rows = useState(Array.from({ length: 10 }, () => ({
            model_code: "",
            suggestions: [],
            showSuggestions: false,
            image_128: null,
            title_color: "",
            product_id: null, // This is product_template_id

            // NEW: Array to hold all variants for this product template
            variants_data: [], // [{ variant_id, attributes_display, qty_available, list_price, wsp_price, quantity_input }]

            // Totals for the row (sum of all variants in this row)
            total_qty: 0,
            total_price: 0,
            total_list_price: 0, // Sum of list prices for selected quantities
        })));

        onWillStart(async () => {
            this.all_products = await this.orm.searchRead("product.product", [],
                ["id", "display_name", "default_code"]);

            if (this.saleOrderId) {
            try {
              const saleOrders = await this.orm.searchRead("sale.order", [["id", "=", this.saleOrderId]],["name"]);
              if (saleOrders && saleOrders.length > 0) {
                this.saleOrderName = saleOrders[0].name // Update the reactive state
              }
                } catch (error) {
                  console.error("Error fetching sale order name:", error)
                  this.notification.add("Failed to load sale order name.", { type: "danger" })
                }
              }
        });
    }

    serialize(obj) {
        return JSON.stringify(obj);
    }

    // MODIFIED: onQuantityChange now targets a specific variant
    onQuantityChange(ev) {
        const rowIndex = parseInt(ev.target.dataset.rowIndex);
        const variantIndex = parseInt(ev.target.dataset.variantIndex);
        const row = this.rows[rowIndex];
        const variant = row.variants_data[variantIndex];

        if (!row.product_id || !variant) {
            this.notification.add("Please select a product and variant first.", { type: "warning" });
            ev.target.value = '';
            return;
        }

        const input = ev.target.value.trim();
        if (input === '') {
            variant.quantity_input = 0;
            this.calculateRowTotals(row);
            return;
        }

        if (!/^\d+$/.test(input)) {
            this.notification.add("Only whole numbers are allowed.", { type: "danger" });
            ev.target.value = '';
            variant.quantity_input = 0;
            this.calculateRowTotals(row);
            return;
        }

        const inputValue = parseInt(input);
        const availableStock = variant.qty_available || 0;

        if (availableStock === 0) {
            this.notification.add("Out of stock for this variant.", { type: "danger" });
            ev.target.value = '';
            variant.quantity_input = 0;
            this.calculateRowTotals(row);
            return;
        }

        if (inputValue > availableStock) {
            this.notification.add(`Only ${availableStock} items in stock for this variant.`, { type: "warning" });
            ev.target.value = availableStock;
            variant.quantity_input = availableStock;
            this.calculateRowTotals(row);
            return;
        }

        variant.quantity_input = inputValue;
        this.calculateRowTotals(row);
    }

    // NEW: onPriceChange method
    onPriceChange(ev) {
        const rowIndex = parseInt(ev.target.dataset.rowIndex);
        const variantIndex = parseInt(ev.target.dataset.variantIndex);
        const row = this.rows[rowIndex];
        const variant = row.variants_data[variantIndex];

        if (!row.product_id || !variant) {
            this.notification.add("Please select a product and variant first.", { type: "warning" });
            ev.target.value = '';
            return;
        }

        const input = ev.target.value.trim();
        if (input === '') {
            variant.list_price = 0; // Or reset to original price if you store it
            variant.wsp_price = 0; // Assuming wsp_price also changes or is derived
            this.calculateRowTotals(row);
            return;
        }

        // Allow decimal numbers for price
        if (!/^\d+(\.\d+)?$/.test(input)) {
            this.notification.add("Please enter a valid number for price.", { type: "danger" });
            ev.target.value = '';
            variant.list_price = 0;
            variant.wsp_price = 0;
            this.calculateRowTotals(row);
            return;
        }

        const inputValue = parseFloat(input);
        if (inputValue < 0) {
            this.notification.add("Price cannot be negative.", { type: "danger" });
            ev.target.value = '';
            variant.list_price = 0;
            variant.wsp_price = 0;
            this.calculateRowTotals(row);
            return;
        }

        variant.list_price = inputValue;
        variant.wsp_price = inputValue; // Assuming wsp_price updates with manual list_price change
        this.calculateRowTotals(row);
    }

//    // MODIFIED: Copy quantities now copies all variant quantities for a row
//    onCopyQuantities(ev) {
//        const rowIndex = parseInt(ev.currentTarget.dataset.rowIndex);
//        const row = this.rows[rowIndex];
//
//        if (!row || !row.product_id) {
//            this.notification.add("Please select a product before copying quantities.", { type: "warning" });
//            return;
//        }
//
//        // Store an array of { variant_id, quantity_input, list_price } for all variants in the row
//        this.copiedQuantities = row.variants_data.map(v => ({
//            variant_id: v.variant_id,
//            quantity_input: v.quantity_input,
//            list_price: v.list_price // Include price in copied data
//        }));
//
//        this.notification.add("Quantities and Prices copied!", { type: "info" });
//    }
//
//    // MODIFIED: Paste quantities now pastes to all matching variants in a row
//    async onPasteQuantities(ev) {
//        const rowIndex = parseInt(ev.currentTarget.dataset.rowIndex);
//        const row = this.rows[rowIndex];
//        if (!row || !row.product_id) {
//            this.notification.add("Please select a product before pasting quantities.", { type: "warning" });
//            return;
//        }
//        if (!this.copiedQuantities) {
//            this.notification.add("No copied quantities found. Please copy from another row first.", { type: "warning" });
//            return;
//        }
//
//        // Apply copied quantities and prices to matching variants in the current row
//        for (const copied of this.copiedQuantities) {
//            const targetVariant = row.variants_data.find(v => v.variant_id === copied.variant_id);
//            if (targetVariant) {
//                const availableStock = targetVariant.qty_available || 0;
//                if (copied.quantity_input > availableStock) {
//                    this.notification.add(`For variant ${targetVariant.attributes_display}, only ${availableStock} in stock. Adjusting quantity...`, { type: "warning" });
//                    targetVariant.quantity_input = availableStock;
//                } else {
//                    targetVariant.quantity_input = copied.quantity_input;
//                }
//                // Paste price
//                targetVariant.list_price = copied.list_price;
//                targetVariant.wsp_price = copied.list_price; // Assuming wsp_price also updates
//            }
//        }
//        this.calculateRowTotals(row);
//        this.notification.add("Quantities and Prices pasted!", { type: "success" });
//    }

    // Existing search functionality
    async onSearchInput(ev) {
        const index = parseInt(ev.target.dataset.rowIndex);
        const value = ev.target.value;
        const row = this.rows[index];
        row.model_code = value;

        if (!value) {
            this.clearRow(row);
            return;
        }

        if (value.length < 0) {
            row.suggestions = [];
            row.showSuggestions = false;
            return;
        }

        const domain = [["model_name", "ilike", value]];
        const fields = ["id", "display_name", "model_name"];
        const templates = await this.orm.searchRead("product.template", domain, fields);

        row.suggestions = templates;
        row.showSuggestions = true;
    }

    showSuggestions(ev) {
        const index = parseInt(ev.target.dataset.rowIndex);
        this.rows[index].showSuggestions = true;
    }

    hideSuggestions(ev) {
        setTimeout(() => {
            const index = parseInt(ev.target.dataset.rowIndex);
            this.rows[index].showSuggestions = false;
        }, 200);
    }

    selectProductFromEvent(ev) {
        const rowIndex = parseInt(ev.currentTarget.dataset.index);
        const product = JSON.parse(ev.currentTarget.dataset.product);
        this.selectProduct(rowIndex, product);
    }

    // MODIFIED: Select product now loads ALL variants for the template
    async selectProduct(rowIndex, productTemplate) {
        const row = this.rows[rowIndex];

        // Clear previous data
        this.clearRow(row);

        // Set basic product info
        row.model_code = productTemplate.model_name;
        row.title_color = productTemplate.display_name;
        row.product_id = productTemplate.id; // This is the product_template_id
        row.suggestions = [];
        row.showSuggestions = false;

        try {
            // NEW: Call a method to get all variants for this product template
            const variantsInfo = await this.orm.call(
                "product.template",
                "get_all_variants_info",
                [productTemplate.id]
            );

            row.image_128 = variantsInfo.image_128;
            row.title_color = variantsInfo.product_name || productTemplate.display_name;

            // Populate variants_data with fetched info, initializing quantity_input
            row.variants_data = variantsInfo.variants.map(v => ({
                ...v,
                quantity_input: 0 // Initialize quantity for each variant
            }));

            this.calculateRowTotals(row); // Recalculate totals after loading variants

        } catch (error) {
            console.error('Error loading product variants:', error);
            this.notification.add("Error loading product variants.", { type: "danger" });
        }
    }

    // MODIFIED: Calculate totals based on all variants in the row
    calculateRowTotals(row) {
        let totalQty = 0;
        let totalPrice = 0;
        let totalListPrice = 0;

        for (const variant of row.variants_data) {
            const quantity = variant.quantity_input || 0;
            // Use the variant's current list_price for calculations
            const price = variant.list_price || 0;

            totalQty += quantity;
            totalPrice += quantity * price;
            totalListPrice += quantity * price; // If list_price is the one being manually changed
        }

        row.total_qty = totalQty;
        row.total_price = parseFloat(totalPrice.toFixed(2));
        row.total_list_price = parseFloat(totalListPrice.toFixed(2));
    }

    // MODIFIED: Add to sale order now iterates through all variants in the row
    async onAddToSaleOrderClick() {
        const linesToAdd = [];
        for (const row of this.rows) {
            if (row.product_id) { // Check if a product template is selected
                for (const variant of row.variants_data) {
                    if (variant.quantity_input > 0) {
                        linesToAdd.push({
                            variant_id: variant.variant_id,
                            quantity: variant.quantity_input,
                            price_unit: variant.list_price // Pass the current price
                        });
                    }
                }
            }
        }

        if (!linesToAdd.length) {
            this.notification.add("No valid product variants with quantities selected.", { type: "warning" });
            return;
        }

        try {
            for (const line of linesToAdd) {
                await this.orm.call(
                    "sale.order",
                    "add_bulk_order_line_with_variant",
                    [this.saleOrderId, line.variant_id, line.quantity, line.price_unit] // Pass price_unit
                );
            }

            this.notification.add("All selected items added to Sale Order", { type: "success" });

            // Clear all rows after adding to sale order
            for (const row of this.rows) {
                this.clearRow(row);
            }

            this.onBackClick();

        } catch (error) {
            console.error('Error adding to sale order:', error);
            this.notification.add("Error adding items to sale order.", { type: "danger" });
        }
    }

    onBackClick() {
        if (this.saleOrderId) this.actionService.restore();
    }

    // MODIFIED: Clear row with new variants_data field
    clearRow(row) {
        row.model_code = "";
        row.suggestions = [];
        row.showSuggestions = false;
        row.image_128 = null;
        row.title_color = "";
        row.product_id = null;

        // Clear variants data
        row.variants_data = [];

        // Clear totals
        row.total_qty = 0;
        row.total_price = 0;
        row.total_list_price = 0;
    }

    onRemoveRowClick(ev) {
        const index = parseInt(ev.currentTarget.dataset.rowIndex);
        const row = this.rows[index];
        this.clearRow(row);
    }

    // MODIFIED: Add single row to sale order now iterates through its variants
    async onAddRowToSaleOrder(ev) {
        const rowIndex = parseInt(ev.currentTarget.dataset.rowIndex);
        const row = this.rows[rowIndex];

        if (!row.product_id) {
            this.notification.add("Product not selected.", { type: "warning" });
            return;
        }

        const variantsToOrder = row.variants_data.filter(v => v.quantity_input > 0);

        if (!variantsToOrder.length) {
            this.notification.add("Please enter quantities for variants before adding to sale order.", { type: "warning" });
            return;
        }

        try {
            for (const variant of variantsToOrder) {
                await this.orm.call(
                    "sale.order",
                    "add_bulk_order_line_with_variant",
                    [this.saleOrderId, variant.variant_id, variant.quantity_input, variant.list_price] // Pass price_unit
                );
            }

            this.notification.add("Selected variants added to Sale Order", { type: "success" });
            this.clearRow(row);

        } catch (error) {
            console.error('Error adding row to sale order:', error);
            this.notification.add("Error adding line to sale order.", { type: "danger" });
        }
    }
}

actionRegistry.add("bulk_order_grid_action", BulkOrderGridComponent);