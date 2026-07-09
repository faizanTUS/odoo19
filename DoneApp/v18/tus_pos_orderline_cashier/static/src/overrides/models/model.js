/** @odoo-module */

import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import {patch} from "@web/core/utils/patch";

patch(PosOrderline.prototype, {
    set_orderline_cashier(cashiers) {
        if (cashiers){
            this.orderline_cashier =cashiers.name;
            this.cashier_id =cashiers.id;
            this.setDirty();
        }
    },

    get_orderline_cashier() {
        return this.orderline_cashier || "";
    },

    getDisplayData() {
        return {
            ...super.getDisplayData(),
            OrderlineCashier: this.get_orderline_cashier() ||"",
        };
    },
});

patch(Orderline, {
    props: {
        ...Orderline.props,
        line: {
            ...Orderline.props.line,
            shape: {
                ...Orderline.props.line.shape,
                OrderlineCashier: { type: String, optional: true },
            },
        },
    },
});