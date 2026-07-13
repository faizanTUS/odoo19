/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/services/pos_store";
import { makeAwaitable } from "@point_of_sale/app/utils/make_awaitable_dialog";
import { SelectComboProductsPopup } from "./select_combo_products_popup/select_combo_products_popup";

function isAdvancedComboProduct(product) {
    return (
        product?.is_combo_product === true &&
        Array.isArray(product?.pos_combo_options) &&
        product.pos_combo_options.length > 0
    );
}

patch(PosStore.prototype, {
    async handleComboProduct(values, order, configure = true, { line } = {}) {
        const productTemplate = values.product_tmpl_id;

        let product = values.product_id;
        if (!product && productTemplate) {
            product = productTemplate.product_variant_ids[0];
        }

        const isAdvancedCombo = isAdvancedComboProduct(product);

        if (isAdvancedCombo && configure) {
            const payload = await makeAwaitable(this.dialog, SelectComboProductsPopup, {
                product,
            });

            if (!payload || !Array.isArray(payload) || payload.length === 0) {
                return false;
            }

            const pricelist = order.pricelist_id;
            let comboPrice = productTemplate.getPrice(pricelist, values.qty || 1, 0, false, product);

            if (!comboPrice || comboPrice === 0) {
                comboPrice = payload.reduce((total, item) => {
                    const childProduct = this.data.models["product.product"].get(item.product_id);
                    return total + (childProduct?.lst_price || 0) * (item.qty || 1);
                }, 0);
            }

            values.price_unit = comboPrice;
            values.price_type = "manual";

            values.combo_line_ids = payload.map((item) => {
                const childProduct = this.data.models["product.product"].get(item.product_id);
                return [
                    "create",
                    {
                        product_id: childProduct,
                        tax_ids: childProduct.taxes_id.map((tax) => ["link", tax]),
                        price_unit: 0,
                        price_type: "original",
                        order_id: order,
                        qty: item.qty,
                    },
                ];
            });

            return true;
        }

        return await super.handleComboProduct(...arguments);
    },

    handlePriceUnit(values, order, price_unit) {
        const product = values.product_id;
        if (isAdvancedComboProduct(product) && values.price_type === "manual" && values.price_unit > 0) {
            return;
        }
        return super.handlePriceUnit(...arguments);
    },
});