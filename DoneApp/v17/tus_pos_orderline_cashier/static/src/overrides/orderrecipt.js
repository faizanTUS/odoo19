/** @odoo-module */

import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import {patch} from "@web/core/utils/patch";
import { omit } from "@web/core/utils/objects";


patch(OrderReceipt.prototype, {
    omit(...args) {
    args[0].receipt = true;
    return omit(...args)
    }
})