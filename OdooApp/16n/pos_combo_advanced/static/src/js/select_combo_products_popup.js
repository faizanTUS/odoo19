odoo.define('pos_combo_advanced.SelectComboProductsPopup', function (require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { useState } = owl;

    class SelectComboProductsPopup extends AbstractAwaitablePopup {

        setup() {
            super.setup();

            const options = this.props.product.pos_combo_options || [];
            const quantities = {};

            for (const opt of options) {
                quantities[opt.product_id] = opt.default_qty || 1;
            }

            this.state = useState({ quantities });

            // Resolve product objects from DB
            this.options = options.map((opt) => ({
                ...opt,
                product: this.env.pos.db.get_product_by_id(opt.product_id),
            })).filter((o) => o.product);
        }

        // ─── Getters ───────────────────────────────────────────────────────────

        get displayMode() {
            return this.props.product.combo_display === 'grid' ? 'grid' : 'list';
        }

        get maxComboItems() {
            return this.props.product.max_combo_items || 0;
        }

        get selectedCount() {
            return Object.values(this.state.quantities)
                .filter(qty => Number(qty) > 0).length;
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
            const currentOrder = this.env.pos.get_order();
            const pricelist = currentOrder ? currentOrder.pricelist : null;

            for (const opt of this.options) {
                const qty = Number(this.state.quantities[opt.product_id] || 0);
                if (qty > 0 && opt.product) {
                    const price = typeof opt.product.get_price === 'function'
                        ? opt.product.get_price(pricelist, qty)
                        : (opt.product.lst_price || 0);
                    total += price * qty;
                }
            }
            return total;
        }

        // ─── Helpers ───────────────────────────────────────────────────────────

        getOptionQty(productId) {
            return Number(this.state.quantities[productId] ?? 0);
        }

        getOptionPrice(opt) {
            const qty = this.getOptionQty(opt.product_id);
            if (!opt.product) return 0;
            const currentOrder = this.env.pos.get_order();
            const pricelist = currentOrder ? currentOrder.pricelist : null;
            const price = typeof opt.product.get_price === 'function'
                ? opt.product.get_price(pricelist, Math.max(qty, 1))
                : (opt.product.lst_price || 0);
            return price * Math.max(qty, 1);
        }

        setOptionQty(productId, qty) {
            const opt = this.options.find((o) => o.product_id === productId);
            if (!opt) return;
            qty = Math.max(0, Math.min(opt.max_qty || 9999, Number(qty) || 0));
            this.state.quantities[productId] = qty;
        }

        increment(productId) {
            // Check max combo items limit before incrementing
            const max = this.maxComboItems;
            if (max > 0 && this.selectedCount >= max) {
                const currentQty = this.getOptionQty(productId);
                // Only allow if this product already has qty > 0 (increasing existing)
                if (currentQty === 0) return;
            }
            this.setOptionQty(productId, this.getOptionQty(productId) + 1);
        }

        decrement(productId) {
            this.setOptionQty(productId, this.getOptionQty(productId) - 1);
        }

        // ─── Actions ───────────────────────────────────────────────────────────

        /**
         * AbstractAwaitablePopup uses getPayload() internally when super.confirm() is called.
         * Never call this.props.close() directly — always use super.confirm() / super.cancel()
         */
        getPayload() {
            return this.options
                .filter((opt) => this.getOptionQty(opt.product_id) > 0)
                .map((opt) => ({
                    product_id: opt.product_id,
                    product: opt.product,
                    qty: this.getOptionQty(opt.product_id),
                    group_name: opt.group_name || '',
                }));
        }

        async confirm() {
            if (!this.canConfirm) return;
            super.confirm();
        }

        async cancel() {
            super.cancel();
        }
    }

    SelectComboProductsPopup.template = 'pos_combo_advanced.SelectComboProductsPopup';
    SelectComboProductsPopup.defaultProps = {
        confirmText: 'Confirm',
        cancelText: 'Cancel',
    };

    Registries.Component.add(SelectComboProductsPopup);
    return SelectComboProductsPopup;
});