/** @odoo-module **/

import {_t} from "@web/core/l10n/translation";
import {ProductScreen} from "@point_of_sale/app/screens/product_screen/product_screen";
import {useService} from "@web/core/utils/hooks";
import {SelectionPopup} from "@point_of_sale/app/utils/input_popups/selection_popup";
import {Component} from "@odoo/owl";
import {usePos} from "@point_of_sale/app/store/pos_hook";

export class OrderlineCashierButton extends Component {
    static template = "point_of_sale.OrderlineCashierButton";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    }

    async onClick() {
        const selectedOrderline = this.pos.get_order().get_selected_orderline();
        if (!selectedOrderline) {
            return;
        }

        const employeesList = this.pos.employee.filter(a => this.pos.config.cashier_ids.includes(a.id)).map((cashier_id) => ({
            id: cashier_id.id,
            label: cashier_id.name,
            item: cashier_id,
        }));

        const {confirmed, payload: inputNote} = await this.popup.add(SelectionPopup, {
            title: _t("Select Cashier"),
            list: employeesList,
        });

        if (confirmed) {
            selectedOrderline.set_orderline_cashier(inputNote);
        }
    }

}

ProductScreen.addControlButton({
    component: OrderlineCashierButton,
});
