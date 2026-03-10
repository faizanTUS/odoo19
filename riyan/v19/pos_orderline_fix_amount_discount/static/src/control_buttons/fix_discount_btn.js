/** @odoo-module **/

import { Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/hooks/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { NumberPopup } from "@point_of_sale/app/components/popups/number_popup/number_popup";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { patch } from "@web/core/utils/patch";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

export class FixDiscountButton extends Component {
    static template = "pos_orderline_fix_amount_discount.FixDiscountButton";
    static props = {};

    setup() {
        this.pos = usePos();
        this.dialog = useService("dialog");
    }
    onClick() {
        const order = this.pos.getOrder();
        const line = order?.getSelectedOrderline();
        if (!line) return;

        const total = line.prices.no_discount_total_excluded;
        if (!total) return;

        this.dialog.add(NumberPopup, {
            title: _t("Discount Amount"),
            startingValue: 0,
            getPayload: (value) => {
                const amount = Math.min(Math.abs(Number(value) || 0), total);
                if (!amount) return;

                line.setDiscountAmount(amount);
            },
        });
    }
}

patch(ControlButtons.prototype, {
    setup() {
        super.setup(...arguments);
        this.constructor.components = {
            ...this.constructor.components,
            FixDiscountButton,
        };
    },
});

patch(PosOrderline.prototype, {

    setDiscountAmount(amount) {
        const total = this.prices.no_discount_total_excluded;
        if (!total) return;

        this.discount_amount = amount;
        this.fixed_discount = true;
        this.discount = (amount / total) * 100;
    },
    setDiscount(discount, { silent = false } = {}) {
        if (this.fixed_discount) {
            return;
        }

        const parsed = Number(discount) || 0;
        this.discount = Math.min(Math.max(parsed, 0), 100);

    },

    set_fixed_discount(flag) {
        this.fixed_discount = !!flag;
    },

    get_fixed_discount() {
        return !!this.fixed_discount;
    },

    set_discount(discount, { silent = false } = {}) {
        if (this.fixed_discount) {
            return;
        }

        const parsed = typeof discount === "number" ? discount : parseFloat(discount) || 0;
        this.discount = Math.min(Math.max(parsed, 0), 100);

    },
});
patch(PaymentScreen.prototype, {
    validateOrder() {
        if (this.currentOrder.get_change) {
            this.currentOrder.getChange = this.currentOrder.get_change.bind(this.currentOrder);
        }
        return super.validateOrder(...arguments);
    },
});