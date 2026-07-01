odoo.define('cash_rounding.PaymentScreen', function(require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const utils = require('web.utils');
    const round_pr = utils.round_precision;

    const SportPodiumPaymentScreen = PaymentScreen => class extends PaymentScreen {
        setup() {
            super.setup()

            this.env.pos.cash_rounding = this.env.pos.cash_rounding_list
        }

        cash_rounding_val(){
            if(this.env.pos.config.cash_rounding) {
                var remaining = this.currentOrder.get_total_with_tax();
                var total = round_pr(remaining, this.cash_rounding.rounding);
                var sign = remaining > 0 ? 1.0 : -1.0;

                var rounding_applied = total - remaining;
                rounding_applied *= sign;
                if (utils.float_is_zero(rounding_applied, this.env.pos.currency.decimal_places)){
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
        }

        on_click_cash_rounding(ev){
            if (this.env.pos.cash_rounding.length){
                $('.cash_rounding_all').removeClass('highlight')
                var selected_rounding =  this.env.pos.cash_rounding_list.filter(function (rounding) {
                    return rounding.id == parseInt($(ev.currentTarget).attr("data-rounding_id"));
                });
                this.env.pos.cash_rounding = selected_rounding
                $(ev.currentTarget).addClass('highlight')
            }
        }
    };

    Registries.Component.extend(PaymentScreen, SportPodiumPaymentScreen);
    return PaymentScreen;
});
