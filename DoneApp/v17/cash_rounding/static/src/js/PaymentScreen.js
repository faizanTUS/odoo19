/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { onWillStart } from "@odoo/owl";
import { roundPrecision as round_pr,floatIsZero } from "@web/core/utils/numbers";

patch(PaymentScreen.prototype, {
    setup() {
            super.setup(...arguments);
            onWillStart(async () => {
                this.cash_rounding_list = await this.env.services.orm.call("account.cash.rounding", "search_read", [[]])
            })
        },
        cash_rounding_val(){
                if(this.pos.config.cash_rounding) {
                    const only_cash = this.pos.config.only_round_cash_method;

                    var remaining = this.currentOrder.get_total_with_tax();
                    var total = round_pr(remaining, this.cash_rounding.rounding);
                    var sign = remaining > 0 ? 1.0 : -1.0;

                    var rounding_applied = total - remaining;
                    rounding_applied *= sign;
                    // because floor and ceil doesn't include decimals in calculation, we reuse the value of the half-up and adapt it.
                    if (floatIsZero(rounding_applied, this.pos.currency.decimal_places)){
                        // https://xkcd.com/217/
                        return this.currentOrder.get_total_with_tax().toFixed(this.currentOrder.pos.currency.decimal_places);
                    } else if(Math.abs(this.currentOrder.get_total_with_tax()) < this.cash_rounding.rounding) {
                        return this.currentOrder.get_total_with_tax().toFixed(this.currentOrder.pos.currency.decimal_places);
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
                    return (this.currentOrder.get_total_with_tax() + (sign * rounding_applied)).toFixed(this.currentOrder.pos.currency.decimal_places);
                }
        },

        on_click_cash_rounding(ev){
                if (this.pos.cash_rounding.length){
//                    $('.cash_rounding_all').removeClass('highlight')
                    var selected_rounding =  this.cash_rounding_list.filter(function (rounding) {return rounding.id == parseInt($(ev.currentTarget).attr("data-rounding_id"))})
                    this.pos['cash_rounding'] = selected_rounding
//                    $(ev.currentTarget).addClass('highlight')
                }
            },

});