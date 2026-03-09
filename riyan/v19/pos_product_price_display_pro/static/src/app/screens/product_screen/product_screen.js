/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { _t } from "@web/core/l10n/translation";

patch(ProductScreen.prototype, {
    getProductPrice(product) {
        const pricelist = this.pos.pricelist;
        const price = product.getPrice(pricelist, 1);

        // Always read fresh from pos.config (reactive store)
        const taxIncluded = this.pos.config?.raw?.iface_tax_included
            ?? this.pos.config?.iface_tax_included;

        if (taxIncluded === "total") {
            const taxes = [...(product.taxes_id?.values?.() ?? [])].filter(Boolean);

            if (taxes.length > 0) {
                const totalTaxAmount = taxes.reduce((sum, tax) => {
                    if (tax.amount_type === "percent") {
                        return sum + (price * tax.amount / 100);
                    }
                    if (tax.amount_type === "fixed") {
                        return sum + tax.amount;
                    }
                    return sum;
                }, 0);

                return this.env.utils.formatCurrency(price + totalTaxAmount);
            }
        }

        return this.env.utils.formatCurrency(price);
    },

    getProductPriceLabel() {
        if (!this.pos?.config) return "";

        // Always read fresh from pos.config (reactive store)
        const taxIncluded = this.pos.config?.raw?.iface_tax_included
            ?? this.pos.config?.iface_tax_included;

        return taxIncluded === "total"
            ? _t("With Tax")
            : _t("Without Tax");
    },
});