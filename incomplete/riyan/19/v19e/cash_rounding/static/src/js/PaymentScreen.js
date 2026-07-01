/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { roundPrecision as round_pr, floatIsZero } from "@web/core/utils/numbers";
import { useState } from "@odoo/owl";


patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.state = useState({
            selected_rounding: false,
        });
        this.pos.cash_rounding = this.pos.cash_rounding_list;
    },

    cash_rounding_val(){
        if(this.pos.config.cash_rounding) {
            var remaining = this.currentOrder.getTotalWithTax();
            var total = round_pr(remaining, this.cash_rounding.rounding);
            var sign = remaining > 0 ? 1.0 : -1.0;

            var rounding_applied = total - remaining;
            rounding_applied *= sign;
            // because floor and ceil doesn't include decimals in calculation, we reuse the value of the half-up and adapt it.
            if (floatIsZero(rounding_applied, this.pos.currency.decimal_places)){
                // https://xkcd.com/217/
                return this.currentOrder.getTotalWithTax().toFixed(this.currentOrder.pos.currency.decimal_places);
            } else if(Math.abs(this.currentOrder.getTotalWithTax()) < this.cash_rounding.rounding) {
                return this.currentOrder.getTotalWithTax().toFixed(this.currentOrder.pos.currency.decimal_places);
            } else if(this.cash_rounding.rounding_method === "UP" && rounding_applied < 0 && remaining > 0) {
                rounding_applied += this.cash_rounding.rounding;
            }
            else if(this.cash_rounding.rounding_method === "UP" && rounding_applied > 0 && remaining < 0) {
                rounding_applied -= this.cash_rounding.rounding;
            }
            else if(this.cash_rounding.rounding_method === "DOWN" && rounding_applied > 0 && remaining > 0){
                rounding_applied -= this.cash_rounding.rounding;
            }
            else if(this.cash_rounding.rounding_method === "DOWN" && rounding_applied < 0 && remaining < 0){
                rounding_applied += this.cash_rounding.rounding;
            }
            return (this.currentOrder.getTotalWithTax() + (sign * rounding_applied)).toFixed(this.pos.currency.decimal_places);
        }
    },

    on_click_cash_rounding(ev){
        var cash_rounding_list = this.pos.models['account.cash.rounding'].getAll();
        if (ev && cash_rounding_list && cash_rounding_list.length){
            var selected_rounding = cash_rounding_list.filter(function (rounding) {
                return rounding.id == parseInt(ev.currentTarget.dataset['rounding_id']);
            });
            this.state.selected_rounding = selected_rounding ? selected_rounding[0].id : 0;
            this.pos.cash_rounding = selected_rounding;
            this.setSelectedRounding(selected_rounding);
            if (selected_rounding) {
                this.pos.config.rounding_method = selected_rounding[0]
            }
            return this.getSelectedRounding();
        }
    },

    setSelectedRounding(selected_rounding) {
        this.state.selected_rounding = selected_rounding[0].id;
    },
    //FIXME remove this
    getSelectedRounding() {
        return this.state.selected_rounding;
    }
});
