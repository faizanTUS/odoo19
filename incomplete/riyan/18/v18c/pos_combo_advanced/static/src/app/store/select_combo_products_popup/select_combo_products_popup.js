/** @odoo-module **/

import { Dialog } from "@web/core/dialog/dialog";
import { Component, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { _t } from "@web/core/l10n/translation";

export class SelectComboProductsPopup extends Component {
    static template = "pos_combo_advanced.SelectComboProductsPopup";
    static components = { Dialog };
    static props = {
        product: Object,
        close: Function,
        getPayload: { type: Function, optional: true },
    };

    setup() {
        this.pos = usePos();
        const options = this.props.product.pos_combo_options ?? this.props.product.raw?.pos_combo_options ?? [];
        const quantities = {};
        for (const opt of options) {
            quantities[opt.product_id] = opt.default_qty || 1;
        }
        this.state = useState({ quantities });
        this.options = options.map((opt) => ({
            ...opt,
            product: this.pos.models["product.product"].get(opt.product_id),
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
        for (const opt of this.options) {
            const qty = Number(this.state.quantities[opt.product_id] || 0);
            if (qty > 0 && opt.product) {
                const price = this.pos.getProductPrice(opt.product) || opt.product.lst_price || 0;
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
        qty = Math.max(0, Math.min(opt.max_qty, Number(qty) || 0));
        this.state.quantities[productId] = qty;
    }

    increment(productId) {
        const opt = this.options.find((o) => o.product_id === productId);
        if (!opt) return;
        const current = this.getOptionQty(productId);
        this.setOptionQty(productId, current + 1);
    }

    decrement(productId) {
        const current = this.getOptionQty(productId);
        this.setOptionQty(productId, current - 1);
    }

    confirm() {
        if (!this.canConfirm) return;
        const selected = this.options
            .filter((opt) => this.getOptionQty(opt.product_id) > 0)
            .map((opt) => ({ product_id: opt.product_id, qty: this.getOptionQty(opt.product_id) }));

        this.props.getPayload(selected);
        this.props.close(selected);
    }

    cancel() {
        this.props.close(null);
    }
}
