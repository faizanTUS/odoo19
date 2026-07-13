/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class SelectComboProductsPopup extends Component {
    static template = "pos_combo_advanced.SelectComboProductsPopup";
    static components = {};
    static props = {
        product: Object,

        // Required by popup service
        close: Function,
        resolve: Function,

        // Injected internally by popup service
        id: { type: Number, optional: true },
        zIndex: { type: Number, optional: true },
        cancelKey: { type: String, optional: true },
        confirmKey: { type: String, optional: true },
    };

    setup() {
        this.pos = usePos();

        const options = this.props.product.pos_combo_options || [];

        const quantities = {};

        for (const opt of options) {
            quantities[opt.product_id] = opt.default_qty || 1;
        }

        this.state = useState({ quantities });

        this.options = options.map((opt) => ({
            ...opt,
            product: this.pos.db.get_product_by_id(opt.product_id),
        })).filter((o) => o.product);
    }

    get displayMode() {
        const product = this.props.product;
        const config = this.pos.config;
        return product.combo_display === "grid" || config.combo_display === "grid" ? "grid" : "list";
    }

    get selectedCount() {
        return Object.entries(this.state.quantities).filter(([, qty]) => Number(qty) > 0).length;
    }

    get maxComboItems() {
        return this.props.product.max_combo_items || 0;
    }

    get isOverMax() {
        const max = this.maxComboItems;
        return max > 0 && this.selectedCount > max;
    }

    get canConfirm() {
        return this.selectedCount > 0 && !this.isOverMax;
    }

    get totalAmount() {
        let total = 0;
        const currentOrder = this.pos.get_order();
        const pricelist = currentOrder ? currentOrder.pricelist : null;

        for (const opt of this.options) {
            const qty = Number(this.state.quantities[opt.product_id] || 0);
            if (qty > 0 && opt.product) {
                const price = typeof opt.product.get_price === "function"
                    ? opt.product.get_price(pricelist, qty)
                    : (opt.product.lst_price || 0);
                total += price * qty;
            }
        }
        return total;
    }

    getOptionQty(productId) {
        return Number(this.state.quantities[productId] ?? 0);
    }

    setOptionQty(productId, qty) {
        const opt = this.options.find((o) => o.product_id === productId);
        if (!opt) return;

        qty = Math.max(0, Math.min(opt.max_qty || 9999, Number(qty) || 0));
        this.state.quantities[productId] = qty;
    }

    increment(productId) {
        this.setOptionQty(productId, this.getOptionQty(productId) + 1);
    }

    decrement(productId) {
        this.setOptionQty(productId, this.getOptionQty(productId) - 1);
    }

    confirm() {
        if (!this.canConfirm) return;
        const selected = this.options
            .filter((opt) => this.getOptionQty(opt.product_id) > 0)
            .map((opt) => ({
                product_id: opt.product_id,
                qty: this.getOptionQty(opt.product_id),
            }));

        this.props.close(selected);
    }

    cancel() {
        this.props.close(null);
    }
}
