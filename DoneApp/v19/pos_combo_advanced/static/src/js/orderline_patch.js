/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Orderline } from "@point_of_sale/app/components/orderline/orderline";

/**
 * FIX: In Odoo 19, the orderline template reads price from:
 *
 *   price: !basic && !line.combo_parent_id && this.line.currencyDisplayPrice
 *
 * For standard Odoo combos, currencyDisplayPrice returns 0 on the parent
 * line because the price is split across child lines.
 *
 * For our advanced combos we keep the full price on the parent line,
 * so we override lineScreenValues in the Orderline COMPONENT to return
 * the real price_unit instead.
 */

function isAdvancedCombo(line) {
    const product = line?.product_id;
    return (
        product?.is_combo_product === true &&
        Array.isArray(product?.pos_combo_options) &&
        product.pos_combo_options.length > 0
    );
}

patch(Orderline.prototype, {
    get lineScreenValues() {
        const values = super.lineScreenValues;

        // Only override for our advanced combo parent lines
        if (isAdvancedCombo(this.line) && !this.line.combo_parent_id) {
            const price = this.line.price_unit ?? 0;
            // Format using the same currency formatter Odoo uses
            const { formatCurrency } = this.env.utils ?? {};
            const formatted = formatCurrency
                ? formatCurrency(price)
                : `${price.toFixed(2)}`;

            return {
                ...values,
                price: formatted,
            };
        }

        return values;
    },
});