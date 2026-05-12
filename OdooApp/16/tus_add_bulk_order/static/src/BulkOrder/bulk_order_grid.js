/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const actionRegistry = registry.category("actions");

export class BulkOrderGridComponent extends Component {
    static template = "BulkOrderGridComponent";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.actionService = useService("action");
        this.saleOrderId = this.props.action.context?.active_id || null;
        this.saleOrderName = "";

        this.rows = useState(
            Array.from({ length: 10 }, () => ({
                model_code: "",
                suggestions: [],
                showSuggestions: false,
                image_128: null,
                title_color: "",
                product_id: null,
                variants_data: [],
                total_qty: 0,
                total_price: 0,
                total_list_price: 0,
            }))
        );

        onWillStart(async () => {
            if (!this.saleOrderId) {
                return;
            }
            try {
                const saleOrders = await this.orm.searchRead(
                    "sale.order",
                    [["id", "=", this.saleOrderId]],
                    ["name"]
                );
                if (saleOrders?.length) {
                    this.saleOrderName = saleOrders[0].name;
                }
            } catch (error) {
                console.error("Error fetching sale order name:", error);
                this.notification.add("Failed to load sale order name.", { type: "danger" });
            }
        });
    }

    serialize(obj) {
        return JSON.stringify(obj);
    }

    onQuantityChange(ev) {
        const rowIndex = Number.parseInt(ev.target.dataset.rowIndex, 10);
        const variantIndex = Number.parseInt(ev.target.dataset.variantIndex, 10);
        const row = this.rows[rowIndex];
        const variant = row.variants_data[variantIndex];

        if (!row.product_id || !variant) {
            this.notification.add("Please select a product and variant first.", { type: "warning" });
            ev.target.value = "";
            return;
        }

        const input = ev.target.value.trim();
        if (input === "") {
            variant.quantity_input = 0;
            this.calculateRowTotals(row);
            return;
        }

        if (!/^\d+$/.test(input)) {
            this.notification.add("Only whole numbers are allowed.", { type: "danger" });
            ev.target.value = "";
            variant.quantity_input = 0;
            this.calculateRowTotals(row);
            return;
        }

        const inputValue = Number.parseInt(input, 10);
        const availableStock = variant.qty_available || 0;

        if (availableStock === 0) {
            this.notification.add("Out of stock for this variant.", { type: "danger" });
            ev.target.value = "";
            variant.quantity_input = 0;
            this.calculateRowTotals(row);
            return;
        }

        if (inputValue > availableStock) {
            this.notification.add(`Only ${availableStock} items in stock for this variant.`, { type: "warning" });
            ev.target.value = String(availableStock);
            variant.quantity_input = availableStock;
            this.calculateRowTotals(row);
            return;
        }

        variant.quantity_input = inputValue;
        this.calculateRowTotals(row);
    }

    onPriceChange(ev) {
        const rowIndex = Number.parseInt(ev.target.dataset.rowIndex, 10);
        const variantIndex = Number.parseInt(ev.target.dataset.variantIndex, 10);
        const row = this.rows[rowIndex];
        const variant = row.variants_data[variantIndex];

        if (!row.product_id || !variant) {
            this.notification.add("Please select a product and variant first.", { type: "warning" });
            ev.target.value = "";
            return;
        }

        const input = ev.target.value.trim();
        if (input === "") {
            variant.list_price = 0;
            variant.wsp_price = 0;
            this.calculateRowTotals(row);
            return;
        }

        if (!/^\d+(\.\d+)?$/.test(input)) {
            this.notification.add("Please enter a valid number for price.", { type: "danger" });
            ev.target.value = "";
            variant.list_price = 0;
            variant.wsp_price = 0;
            this.calculateRowTotals(row);
            return;
        }

        const inputValue = Number.parseFloat(input);
        if (inputValue < 0) {
            this.notification.add("Price cannot be negative.", { type: "danger" });
            ev.target.value = "";
            variant.list_price = 0;
            variant.wsp_price = 0;
            this.calculateRowTotals(row);
            return;
        }

        variant.list_price = inputValue;
        variant.wsp_price = inputValue;
        this.calculateRowTotals(row);
    }

    async onSearchInput(ev) {
        const index = Number.parseInt(ev.target.dataset.rowIndex, 10);
        const value = ev.target.value;
        const row = this.rows[index];
        row.model_code = value;

        if (!value) {
            this.clearRow(row);
            return;
        }

        const domain = [["model_name", "ilike", value]];
        const fields = ["id", "display_name", "model_name"];
        const templates = await this.orm.searchRead("product.template", domain, fields);

        row.suggestions = templates;
        row.showSuggestions = true;
    }

    showSuggestions(ev) {
        const index = Number.parseInt(ev.target.dataset.rowIndex, 10);
        this.rows[index].showSuggestions = true;
    }

    hideSuggestions(ev) {
        setTimeout(() => {
            const index = Number.parseInt(ev.target.dataset.rowIndex, 10);
            this.rows[index].showSuggestions = false;
        }, 200);
    }

    selectProductFromEvent(ev) {
        const rowIndex = Number.parseInt(ev.currentTarget.dataset.index, 10);
        const product = JSON.parse(ev.currentTarget.dataset.product);
        this.selectProduct(rowIndex, product);
    }

    async selectProduct(rowIndex, productTemplate) {
        const row = this.rows[rowIndex];

        this.clearRow(row);

        row.model_code = productTemplate.model_name;
        row.title_color = productTemplate.display_name;
        row.product_id = productTemplate.id;
        row.suggestions = [];
        row.showSuggestions = false;

        try {
            const variantsInfo = await this.orm.call(
                "product.template",
                "get_all_variants_info",
                [productTemplate.id]
            );

            row.image_128 = variantsInfo.image_128;
            row.title_color = variantsInfo.product_name || productTemplate.display_name;

            row.variants_data = variantsInfo.variants.map((v) => ({
                ...v,
                quantity_input: 0,
            }));

            this.calculateRowTotals(row);
        } catch (error) {
            console.error("Error loading product variants:", error);
            this.notification.add("Error loading product variants.", { type: "danger" });
        }
    }

    calculateRowTotals(row) {
        let totalQty = 0;
        let lineTotal = 0;

        for (const variant of row.variants_data) {
            const quantity = variant.quantity_input || 0;
            const price = variant.list_price || 0;
            totalQty += quantity;
            lineTotal += quantity * price;
        }

        const rounded = Number.parseFloat(lineTotal.toFixed(2));
        row.total_qty = totalQty;
        row.total_price = rounded;
        row.total_list_price = rounded;
    }

    async onAddToSaleOrderClick() {
        const linesToAdd = [];
        for (const row of this.rows) {
            if (row.product_id) {
                for (const variant of row.variants_data) {
                    if (variant.quantity_input > 0) {
                        linesToAdd.push({
                            variant_id: variant.variant_id,
                            quantity: variant.quantity_input,
                            price_unit: variant.list_price,
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
                await this.orm.call("sale.order", "add_bulk_order_line_with_variant", [
                    this.saleOrderId,
                    line.variant_id,
                    line.quantity,
                    line.price_unit,
                ]);
            }

            this.notification.add("All selected items added to Sale Order", { type: "success" });

            for (const row of this.rows) {
                this.clearRow(row);
            }

            this.onBackClick();
        } catch (error) {
            console.error("Error adding to sale order:", error);
            this.notification.add("Error adding items to sale order.", { type: "danger" });
        }
    }

    onBackClick() {
        if (!this.saleOrderId) {
            return;
        }
        this.actionService.doAction(
            {
                type: "ir.actions.act_window",
                res_model: "sale.order",
                views: [[false, "form"]],
                res_id: this.saleOrderId,
                target: "self",
            },
            { clearBreadcrumbs: true }
        );
    }

    clearRow(row) {
        row.model_code = "";
        row.suggestions = [];
        row.showSuggestions = false;
        row.image_128 = null;
        row.title_color = "";
        row.product_id = null;
        row.variants_data = [];
        row.total_qty = 0;
        row.total_price = 0;
        row.total_list_price = 0;
    }

    onRemoveRowClick(ev) {
        const index = Number.parseInt(ev.currentTarget.dataset.rowIndex, 10);
        this.clearRow(this.rows[index]);
    }

    async onAddRowToSaleOrder(ev) {
        const rowIndex = Number.parseInt(ev.currentTarget.dataset.rowIndex, 10);
        const row = this.rows[rowIndex];

        if (!row.product_id) {
            this.notification.add("Product not selected.", { type: "warning" });
            return;
        }

        const variantsToOrder = row.variants_data.filter((v) => v.quantity_input > 0);

        if (!variantsToOrder.length) {
            this.notification.add(
                "Please enter quantities for variants before adding to sale order.",
                { type: "warning" }
            );
            return;
        }

        try {
            for (const variant of variantsToOrder) {
                await this.orm.call("sale.order", "add_bulk_order_line_with_variant", [
                    this.saleOrderId,
                    variant.variant_id,
                    variant.quantity_input,
                    variant.list_price,
                ]);
            }

            this.notification.add("Selected variants added to Sale Order", { type: "success" });
            this.clearRow(row);
        } catch (error) {
            console.error("Error adding row to sale order:", error);
            this.notification.add("Error adding line to sale order.", { type: "danger" });
        }
    }
}

actionRegistry.add("bulk_order_grid_action", BulkOrderGridComponent);
