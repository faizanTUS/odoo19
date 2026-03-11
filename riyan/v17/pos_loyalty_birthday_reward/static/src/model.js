/* @odoo-module */

import { Order, Orderline } from "@point_of_sale/app/store/models";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";

patch(Orderline.prototype, {
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.set_birthday(json.is_birthday);
    },

    export_as_JSON(){
        const json = super.export_as_JSON(...arguments);
        json.is_birthday = this.is_birthday;
        return json;
    },
})

patch(Order.prototype, {
    set_orderline_options(line, options) {
        super.set_orderline_options(...arguments);
        line.is_birthday = options.is_birthday;
    },

})