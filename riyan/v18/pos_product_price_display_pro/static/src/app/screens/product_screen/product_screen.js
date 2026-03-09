/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { _t } from "@web/core/l10n/translation";

patch(ProductScreen.prototype, {
    /**
     * Returns the "With Tax" or "Without Tax" label depending on POS config.
     * The actual price is computed by the base getProductPrice() method
     * which already respects iface_tax_included, pricelists, and fiscal positions.
     */
    getProductPriceLabel() {
        if (!this.pos?.config) return "";
        return this.pos.config.iface_tax_included === "total"
            ? _t("With Tax")
            : _t("Without Tax");
    },
});
