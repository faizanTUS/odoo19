/** @odoo-module **/

import { PosOrder } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { omit } from "@web/core/utils/objects";

patch(PosOrder.prototype, "pos_combo_export", {
    export_for_printing(baseUrl, headerData) {
        const result = super.export_for_printing(baseUrl, headerData);

        const orderlines = this.getSortedOrderlines().map((l) => {
            const data = omit(l.getDisplayData(), "internalNote");

            data.id = l.id;
            data.is_combo_parent = l.combo_line_ids?.length > 0;
            data.is_combo_child = !!l.combo_parent_id;
            data.combo_parent_id = l.combo_parent_id?.id || null;

            return data;
        });

        result.orderlines = orderlines;
        result.has_combo = orderlines.some(l => l.is_combo_parent);

        return result;
    },
});




/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/services/pos_store";
import { makeAwaitable } from "@point_of_sale/app/utils/make_awaitable_dialog";
import { SelectComboProductsPopup } from "./select_combo_products_popup/select_combo_products_popup";

const originalAddLineToOrder = PosStore.prototype.addLineToOrder;

function isAdvancedComboProduct(product) {
    if (!product) return false;
    const isCombo = product.is_combo_product === true || product.raw?.is_combo_product === true;
    const options = product.pos_combo_options ?? product.raw?.pos_combo_options;
    return isCombo && Array.isArray(options) && options.length > 0;
}

patch(PosStore.prototype, {
    async addLineToOrder(vals, order, opts = {}, configure = true) {
        const product = typeof vals.product_id === "number"
            ? this.data.models["product.product"].get(vals.product_id)
            : vals.product_id;

        if (isAdvancedComboProduct(product) && configure) {
            const payload = await makeAwaitable(this.dialog, SelectComboProductsPopup, {
                product,
            });
            if (!payload) return;

            const currentOrder = order || this.get_order() || this.add_new_order();

            // Get price - try multiple methods
            let parentPrice = product.lst_price || 0;
            try {
                if (typeof product.getPrice === "function") {
                    parentPrice = product.getPrice(currentOrder.pricelist_id, vals.qty || 1, 0, false, product);
                } else if (typeof product.get_price === "function") {
                    parentPrice = product.get_price(currentOrder.pricelist_id, vals.qty || 1);
                }
            } catch(e) { /* use lst_price fallback */ }


            // Add parent line with configure=false, price_type="original" (NOT manual/combo)
            const parentLine = await originalAddLineToOrder.call(this, {
                ...vals,
                price_unit: parentPrice,
                price_type: "original",
                merge: false,
            }, currentOrder, opts, false);

            if (!parentLine) return;

            // Add child lines manually
            for (const item of payload) {
                const childProduct = this.data.models["product.product"].get(item.product_id);
                if (!childProduct) continue;

                await originalAddLineToOrder.call(this, {
                    product_id: childProduct,
                    qty: item.qty,
                    price_unit: 0,
                    price_type: "original",
                    merge: false,
                }, currentOrder, opts, false);
            }

            return parentLine;
        }

        return await originalAddLineToOrder.apply(this, arguments);
    },
});
