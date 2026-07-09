/** @odoo-module */

import {Order, Orderline} from "@point_of_sale/app/store/models";
import {patch} from "@web/core/utils/patch";

patch(Orderline.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
        this.orderline_cashier = this.orderline_cashier || this.cashier;
    },
    set_orderline_cashier(orderline_cashier) {
        this.orderline_cashier_id = orderline_cashier.id;
        this.orderline_cashier = orderline_cashier.name;
    },

    get_orderline_cashier(orderline_cashier) {
        return this.orderline_cashier;
    },

    //@override
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.orderline_cashier = this.orderline_cashier;
        return json;
    },
    //@override
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.orderline_cashier = json.orderline_cashier;
    },

    getDisplayData() {
        return {
            ...super.getDisplayData(),
            orderline_cashier: this.orderline_cashier,
        };
    },
});
