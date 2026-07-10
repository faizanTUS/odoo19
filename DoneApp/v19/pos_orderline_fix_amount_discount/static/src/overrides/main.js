/** @odoo-module **/

import { Orderline } from "@point_of_sale/app/components/orderline/orderline";
import { patch } from "@web/core/utils/patch";

patch(Orderline.prototype, {
    get discountAmountNumber() {
        const vals = this.lineScreenValues;

        if (!vals?.noDiscountPrice || !vals?.price) {
            return 0;
        }

        const noDiscount = Number(
            String(vals.noDiscountPrice).replace(/[^0-9.-]/g, "")
        ) || 0;

        const price = Number(
            String(vals.price).replace(/[^0-9.-]/g, "")
        ) || 0;
        return Math.round(noDiscount - price);
    },
});
