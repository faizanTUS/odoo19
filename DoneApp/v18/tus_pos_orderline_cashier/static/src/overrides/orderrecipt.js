/** @odoo-module */

import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import {patch} from "@web/core/utils/patch";
import { omit } from "@web/core/utils/objects";
import { Component } from "@odoo/owl";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";

patch(PosOrderline.prototype, {
    setup(vals) {
        this.receipt = false;
        return super.setup(...arguments);
    },
});

patch(Orderline, {
    props: {
        ...Orderline.props,  // Spread the existing props
        line: {
            type: Object,
            shape: {
                ...Orderline.props.line.shape,  // Spread the existing shape of `line`
                receipt: { type: Boolean, optional: true },  // Add the `receipt` field
            },
        },
    },
});

patch(OrderReceipt.prototype, {
    omit(...args) {
    args[0].receipt = true;
    return omit(...args)
    }
})