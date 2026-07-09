/** @odoo-module */

import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
//import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { Orderline } from "@point_of_sale/app/components/orderline/orderline";
import { OrderDisplay } from "@point_of_sale/app/components/order_display/order_display";

import {patch} from "@web/core/utils/patch";

patch(PosOrderline.prototype, {
    set_orderline_cashier(cashiers) {
    debugger;
        if (cashiers){
            this.orderline_cashier =cashiers.name;
            this.cashier_id =cashiers.id;
//            this.setDirty();
            this._markDirty();
        }
    },

    get_orderline_cashier() {
        return this.orderline_cashier || "";
    },

//    getDisplayData() {
//        return {
//            ...super.getDisplayData(),
//            OrderlineCashier: this.get_orderline_cashier() ||"",
//        };
//    },
});

patch(Orderline.prototype, {
    props: {
        ...Orderline.props,
        line: {
            ...Orderline.props.line,
            shape: {
                ...Orderline.props.line.shape,
                orderline_cashier: { type: String, optional: true },
            },
        },
    },
});