/** @odoo-module **/

import { Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { patch } from "@web/core/utils/patch";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";

export class FixDiscountButton extends Component {
    static template = "pos_orderline_fix_amount_discount.FixDiscountButton";
    static props = {};

    setup() {
        this.pos = usePos();
        this.dialog = useService("dialog");
    }

    onClick() {
        const order = this.pos.get_order();
        const line  = order?.get_selected_orderline();
        if (!line) return;

        const total = line.get_unit_price() * line.get_quantity();
        if (!total) return;

        this.dialog.add(NumberPopup, {
            title: _t("Discount Amount"),
            startingValue: 0,
            getPayload: (value) => {
                const amount = Math.min(Math.abs(parseFloat(value) || 0), total);
                if (!amount) return;
                line.set_discount_amount(amount);
                line.set_fixed_discount(true);
                order.recomputeOrderData();
            },
        });
    }
}

/*  register button  */
patch(ControlButtons.prototype, {
    setup() {
        super.setup(...arguments);
        this.constructor.components = {
            ...this.constructor.components,
            FixDiscountButton,
        };
    },
});

/*  data model  */
patch(PosOrderline.prototype, {

    set_discount_amount(amount) {
        const qty = this.get_quantity();
        if (!qty) return;

        if (!this._original_unit_price) {
            this._original_unit_price = this.get_unit_price();
        }

        const total = this._original_unit_price * qty;
        if (!total) return;

        this.discount_amount = amount;
        this.fixed_discount = true;

        // % only for calculations
        this.discount = (amount / total) * 100;

        this.order_id.recomputeOrderData();
        this.setDirty();
    },

    set_fixed_discount(flag) {
        this.fixed_discount = !!flag;
    },

    get_fixed_discount() {
        return !!this.fixed_discount;
    },

    set_discount(discount, { silent = false } = {}) {
        if (this.fixed_discount) {
            if (!silent) this.order_id.recomputeOrderData();
            this.setDirty();
            return;
        }

        const parsed = typeof discount === "number" ? discount : parseFloat(discount) || 0;
        this.discount = Math.min(Math.max(parsed, 0), 100);

        if (!silent) this.order_id.recomputeOrderData();
        this.setDirty();
    },
});