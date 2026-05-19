/** @odoo-module **/

import { Dialog } from "@web/core/dialog/dialog";
import { Component, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/hooks/pos_hook";

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
        const options = this.props.product.pos_combo_options ?? [];
        const quantities = {};
        for (const opt of options) {
            quantities[opt.product_id] = opt.default_qty || 1;
        }
        this.state = useState({ quantities });
        this.options = options.map((opt) => ({
            ...opt,
            product: this.pos.data.models["product.product"].get(opt.product_id),
        })).filter((o) => o.product);
    }

    get displayMode() {
        return this.props.product.combo_display === "grid" ? "grid" : "list";
    }

    get selectedCount() {
        return Object.values(this.state.quantities).filter((qty) => Number(qty) > 0).length;
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
                total += (opt.product.lst_price || 0) * qty;
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
        qty = Math.max(0, Math.min(opt.max_qty || 99, Number(qty) || 0));
        this.state.quantities[productId] = qty;
    }

    increment(productId) {
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
            .map((opt) => ({
                product_id: opt.product_id,
                qty: this.getOptionQty(opt.product_id),
            }));
        // getPayload is how makeAwaitable receives the return value in Odoo 19
        // It must be called BEFORE close()
        if (this.props.getPayload) {
            this.props.getPayload(selected);
        }
        this.props.close();
    }

    cancel() {
        if (this.props.getPayload) {
            this.props.getPayload(null);
        }
        this.props.close();
    }
}