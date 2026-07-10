/** @odoo-module **/

import { Orderline } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { roundPrecision } from "@web/core/utils/numbers";


patch(Orderline.prototype, {

    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.set_discount_amount(json.discount_amount);
    },

    export_as_JSON(){
        const json = super.export_as_JSON(...arguments);
        json.discount_amount = this.discount_amount;
        return json;
    },

    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        result.discount_amount = this.discount_amount;
        return result
    },


    getDisplayData() {
        return {
            ...super.getDisplayData(),
            discount_amount: this.discount_amount ? roundPrecision(this.discount_amount, 0.01) : 0,
            discount_amount_formatted: this.discount_amount ? this.env.utils.formatCurrency(this.get_discount_amount()) : this.env.utils.formatCurrency(0),
        };
    },

    clone() {
        const orderline = super.clone(...arguments);
        orderline.discount_amount = this.discount_amount
        return order_line
    },

    set_discount_amount(amount){
        this.discount_amount = amount;
    },

    get_discount_amount(){
        return this.discount_amount;
    },

    get_all_prices(qty = this.get_quantity()) {
        var price_unit = (this.get_unit_price() * (1.0 - this.get_discount() / 100.0));
        var taxtotal = 0;
        var product = this.get_product();
        var taxes_ids = this.tax_ids || product.taxes_id;
        taxes_ids = taxes_ids.filter((t) => t in this.pos.taxes_by_id);
        var taxdetail = {};
        var product_taxes = this.pos.get_taxes_after_fp(taxes_ids, this.order.fiscal_position);

        var all_taxes = this.compute_all(
            product_taxes,
            price_unit,
            qty,
            this.pos.currency.rounding
        );
        var all_taxes_before_discount = this.compute_all(
            product_taxes,
            this.get_unit_price(),
            qty,
            this.pos.currency.rounding
        );
        all_taxes.taxes.forEach(function (tax) {
            taxtotal += tax.amount;
            taxdetail[tax.id] = {
                amount: tax.amount,
                base: tax.base,
            };
        });

        return {
            priceWithTax: all_taxes.total_included - (this.get_discount_amount() || 0),
            priceWithoutTax: all_taxes.total_excluded - (this.get_discount_amount() || 0),
            priceWithTaxBeforeDiscount: all_taxes_before_discount.total_included,
            priceWithoutTaxBeforeDiscount: all_taxes_before_discount.total_excluded,
            tax: taxtotal,
            taxDetails: taxdetail,
        };
    },

})