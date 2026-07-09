/** @odoo-module **/

import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { patch } from "@web/core/utils/patch";

patch(Orderline.prototype, {
    removecashier() {
        this.env.services.pos.get_order().selected_orderline.orderline_cashier = "";
    },
});
