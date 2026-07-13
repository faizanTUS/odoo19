/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { SelectComboProductsPopup } from "./select_combo_products_popup/select_combo_products_popup";

function isAdvancedComboProduct(product) {
    if (!product) return false;
    const isCombo = product.is_combo_product === true || product.raw?.is_combo_product === true;
    const options = product.pos_combo_options ?? product.raw?.pos_combo_options;
    return isCombo && Array.isArray(options) && options.length > 0;
}

const originalAddLineToOrder = PosStore.prototype.addProductToCurrentOrder;

patch(PosStore.prototype, {
    async addProductToCurrentOrder(product, options = {}) {
        const realProduct =
            typeof product === "number"
                ? this.data.models["product.product"].get(product)
                : product;

        // POS Combo Products (advanced): custom combo popup and child lines
        if (isAdvancedComboProduct(realProduct)) {
            const payload = await this.env.services.popup.add(
                SelectComboProductsPopup,
                { product: realProduct }
            )
            if (!payload) {
                return;
            }

            const currentOrder = this.get_order();

            const parentPrice = typeof realProduct.get_price === "function"
                ? realProduct.get_price(currentOrder.pricelist, options.quantity || 1)
                : (realProduct.lst_price || 0);

            await super.addProductToCurrentOrder(realProduct, {
                ...options,
                merge: false,
            });

            const parentLine = currentOrder.get_selected_orderline();

            if (parentLine) {
                parentLine.price_unit = parentPrice;
                parentLine.is_combo_parent = true;
                parentLine.combo_line_ids = [];
            }

            // Add child lines
            if (parentLine && payload.length) {
                for (const item of payload) {
                    const childProduct = typeof product === "number"
                        ? this.data.models["product.product"].get(item.product_id)
                        : item.product_id;

                    if (childProduct) {

                        await super.addProductToCurrentOrder(childProduct, {
                            quantity:   item.qty,
                            price_unit: 0,
                            merge:      false,
                        });

                        const childLine = currentOrder.get_selected_orderline();

                        if (childLine) {
                            childLine.set_unit_price(0);
                            parentLine.is_combo_parent = false;
                            childLine.is_combo_child = true
                            childLine.combo_parent_id = parentLine;
                            parentLine.combo_line_ids.push(childLine);
                        }
                    }
                }
            }
            return parentLine;
        }
        // Normal behavior
        return await super.addProductToCurrentOrder(product, options);
    },
});
