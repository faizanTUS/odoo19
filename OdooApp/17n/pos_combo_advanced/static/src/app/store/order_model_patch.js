/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Orderline, Order } from "@point_of_sale/app/store/models";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { useRef, onMounted, onPatched } from "@odoo/owl";

patch(Orderline.prototype, {

    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.is_combo_parent    = json.is_combo_parent   ?? false;
        this.is_combo_child     = json.is_combo_child    ?? false;
        this._combo_parent_uuid = json.combo_parent_uuid ?? null;
    },

    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.is_combo_parent   = this.is_combo_parent   ?? false;
        json.is_combo_child    = this.is_combo_child    ?? false;
        json.combo_parent_uuid = this.combo_parent_id?.uuid ?? null;
        return json;
    },

    getDisplayClasses() {
        const classes = super.getDisplayClasses ? super.getDisplayClasses() : {};
        if (this.is_combo_parent) {
            classes["combo-product"]   = true;
            classes["is-combo-parent"] = true;
        }
        if (this.is_combo_child) {
            classes["is-combo-child"]  = true;
        }
        return classes;
    },

    getDisplayData() {
        const data = super.getDisplayData(...arguments);
        data.is_combo_parent = this.is_combo_parent ?? false;
        data.is_combo_child  = this.is_combo_child  ?? false;
        return data;
    },
});

patch(Order.prototype, {

    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this._relinkComboLines();
    },

    _relinkComboLines() {
        const lineByUuid = {};
        this.orderlines.forEach((line) => {
            if (line.uuid) lineByUuid[line.uuid] = line;
        });
        this.orderlines.forEach((line) => {
            if (line._combo_parent_uuid) {
                const parent = lineByUuid[line._combo_parent_uuid];
                if (parent) {
                    line.combo_parent_id = parent;
                    if (!parent.combo_line_ids) parent.combo_line_ids = [];
                    if (!parent.combo_line_ids.includes(line)) {
                        parent.combo_line_ids.push(line);
                    }
                }
            }
        });
    },

    export_for_printing(baseUrl, headerData) {
        const result = super.export_for_printing(baseUrl, headerData);

        const allLines = [];
        this.orderlines.forEach((line) => allLines.push(line));

        const orderlines = allLines.map((line) => {
            const data = { ...line.getDisplayData() };
            delete data.internalNote;

            data.id                = line.id;
            data.uuid              = line.uuid;
            data.is_combo_parent   = line.is_combo_parent  ?? false;
            data.is_combo_child    = line.is_combo_child   ?? false;
            data.combo_parent_uuid = line.combo_parent_id?.uuid ?? null;

            if (line.is_combo_child) {
                data.price             = "$ 0.00";
                data.price_with_tax    = "$ 0.00";
                data.price_without_tax = "$ 0.00";
                data.unitPrice         = "$ 0.00";
                data.old_unit_price    = "$ 0.00";
            }

            return data;
        });

        result.orderlines = orderlines;
        result.has_combo  = orderlines.some((l) => l.is_combo_parent);
        return result;
    },
});

patch(OrderReceipt.prototype, {
    setup() {
        super.setup(...arguments);

        const applyComboClasses = () => {
            // Get the root DOM node of this component
            const root = this.__owl__.bdom?.el || this.el;
            if (!root) return;

            const orderlines = this.props?.data?.orderlines ?? [];
            if (!orderlines.length) return;

            // .orderline elements rendered inside the receipt
            const els = root.querySelectorAll(".orderline");
            if (!els.length) return;

            els.forEach((el, idx) => {
                const line = orderlines[idx];
                if (!line) return;

                el.classList.remove("combo-parent-receipt", "combo-child-receipt");

                if (line.is_combo_parent) el.classList.add("combo-parent-receipt");
                if (line.is_combo_child)  el.classList.add("combo-child-receipt");
            });
        };

        onMounted(applyComboClasses);
        onPatched(applyComboClasses);
    },
});


