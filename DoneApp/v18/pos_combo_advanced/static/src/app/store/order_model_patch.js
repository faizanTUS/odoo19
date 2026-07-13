/** @odoo-module **/

import { PosOrder } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { omit } from "@web/core/utils/objects";

patch(PosOrder.prototype, "pos_combo_export", {
    export_for_printing(baseUrl, headerData) {
        const result = super.export_for_printing(baseUrl, headerData);

        const orderlines = this.getSortedOrderlines().map((l) => {
            const data = omit(l.getDisplayData(), "internalNote");

            data.id = l.id;
            data.is_combo_parent = l.combo_line_ids?.length > 0;
            data.is_combo_child = !!l.combo_parent_id;
            data.combo_parent_id = l.combo_parent_id?.id || null;

            return data;
        });

        result.orderlines = orderlines;
        result.has_combo = orderlines.some(l => l.is_combo_parent);

        return result;
    },
});
