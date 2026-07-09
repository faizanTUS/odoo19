/** @odoo-module **/

import {_t} from "@web/core/l10n/translation";
import {ProductScreen} from "@point_of_sale/app/screens/product_screen/product_screen";
import {useService} from "@web/core/utils/hooks";
import {SelectionPopup} from "@point_of_sale/app/utils/input_popups/selection_popup";
import {Component} from "@odoo/owl";
import {usePos} from "@point_of_sale/app/store/pos_hook";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";

patch(PosStore.prototype, {

    // @Override
    async selectCashier() {
        let self = this;
        const selectedOrderline = this.get_order().get_selected_orderline();
        let cashier_ids = self.config.cashier_ids;
        if (!selectedOrderline) {
            return;
        }
        const allEmployees = self.env.services.pos.models["hr.employee"].filter(
            (employee) => employee.id !== self.env.services.pos.config.cashier_ids.id
        );

        const prepareList = (employees) => 
            self.env.services.pos.config.cashier_ids.map(employee => ({
                id: employee.id,
                item: employee,
                label: employee.name,
                isSelected: false
            }));

        const employeesList = self.env.services.pos.models["hr.employee"]
            .filter(employee => self.env.services.pos.config.cashier_ids.includes(employee.id));

        
        const payload = await makeAwaitable(this.dialog, SelectionPopup, {
                title: _t("Change Cashier"),
                list: prepareList(self.env.services.pos.config.cashier_ids),
            });

        const selectedCashier = this.defaultProps.getter(selectedOrderline);

        self.defaultProps.setter(selectedOrderline, payload);
        return { confirmed: typeof payload === "string", inputNote: payload };
    },
});
PosStore.props = {
    icon: { type: String, optional: true },
    label: { type: String, optional: true },
    getter: { type: Function, optional: true },
    setter: { type: Function, optional: true },
    class: { type: String, optional: true },
};
// Static defaultProps
PosStore.prototype.defaultProps = {
    label: _t("Cashier"),
    getter: (orderline) => orderline.get_orderline_cashier(),
    setter: (orderline, cashiers) => orderline.set_orderline_cashier(cashiers),
    class: "",
};