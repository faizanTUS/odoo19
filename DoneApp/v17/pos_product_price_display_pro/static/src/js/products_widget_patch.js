/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ProductsWidget } from "@point_of_sale/app/screens/product_screen/product_list/product_list";
import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";
import { _t } from "@web/core/l10n/translation";

// Add priceLabel to ProductCard's accepted props
patch(ProductCard, {
    props: {
        ...ProductCard.props,
        priceLabel: { type: String, optional: true },
    },
});

patch(ProductsWidget.prototype, {
    getProductPrice(product) {
        const pos = this.pos;
        const pricelist = pos.get_order?.()?.pricelist ?? null;

        // Odoo 17 uses get_price, not getPrice
        const price = product.get_price(pricelist, 1);
        const taxIncluded = pos.config?.iface_tax_included;

        if (taxIncluded === "total") {
            const taxes = (product.taxes_id || [])
                .map(id => pos.taxes_by_id?.[id])
                .filter(Boolean);

            if (taxes.length > 0) {
                const taxFactor = taxes.reduce((f, tax) => {
                    if (tax.amount_type === "percent") return f + tax.amount / 100;
                    return f;
                }, 0);
                return this.env.utils.formatCurrency(price * (1 + taxFactor));
            }
        }
        return this.env.utils.formatCurrency(price);
    },

    getPriceLabel() {
        const taxIncluded = this.pos?.config?.iface_tax_included;
        return taxIncluded === "total" ? _t("With Tax") : _t("Without Tax");
    },
});