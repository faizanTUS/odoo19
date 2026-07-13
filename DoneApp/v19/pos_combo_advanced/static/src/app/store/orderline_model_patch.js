/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { SelectComboProductsPopup } from "./select_combo_products_popup/select_combo_products_popup";

const originalAddLineToOrder = PosStore.prototype.addLineToOrder;

function isAdvancedComboProduct(product) {
    debugger;
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
        debugger;
        // POS Combo Products (advanced): custom combo popup and child lines
        if (isAdvancedComboProduct(product) && configure) {
            const payload = await makeAwaitable(this.dialog, SelectComboProductsPopup, {
                product,
            });
            if (!payload) {
                return;
            }

            const currentOrder = order || this.get_order() || this.add_new_order();

            // Add the parent line (force configure=false to avoid recursion)
            const parentPrice = typeof product.get_price === "function"
                ? product.get_price(currentOrder.pricelist_id, vals.qty || 1)
                : this.getProductPrice(product);

            // Add the parent line (force configure=false to avoid recursion)
            const parentLine = await originalAddLineToOrder.call(this, {
                ...vals,
                price_unit: typeof parentPrice === "number" ? parentPrice : (product.lst_price || 0),
                merge: false,
            }, currentOrder, opts, false);

            if (parentLine) {
                parentLine.price_unit = parentPrice;
                parentLine.is_combo_parent = true;
                parentLine.combo_line_ids = [];
            }

            if (parentLine && payload.length) {
                for (const item of payload) {
                    const childProduct = this.data.models["product.product"].get(item.product_id);
                    if (childProduct) {
                        const childLine = await this.addLineToOrder({
                            product_id: childProduct,
                            qty: item.qty,
                            price_unit: 0,
                            merge: false,
                        }, currentOrder, { ...opts, combo_parent_id: parentLine }, false);
                        if (childLine) {
                            childLine.combo_parent_id = parentLine;
                            parentLine.combo_line_ids.push(childLine);
                        }
                    }
                }
            }
            return parentLine;
        }

        return await originalAddLineToOrder.apply(this, arguments);
    },
});
