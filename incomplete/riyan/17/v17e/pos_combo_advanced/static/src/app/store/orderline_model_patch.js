/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Orderline } from "@point_of_sale/app/store/models";

patch(Orderline.prototype, {
    get isComboChild() {
        return this.is_combo_childLine === true;
    },
    getDisplayData() {
        return {
            ...super.getDisplayData(),
            is_combo_child: this.is_combo_childLine,
        };
    },

});