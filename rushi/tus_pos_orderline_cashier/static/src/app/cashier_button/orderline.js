/** @odoo-module **/

import { Orderline } from "@point_of_sale/app/components/orderline/orderline";
import { patch } from "@web/core/utils/patch";

patch(Orderline.prototype,{
    async usericonclick() {
        const employeesList = this.env.pos.employee
            .filter((employee) =>
                this.env.pos.config.cashier_ids.includes(employee.id)
            )
            .map((employee) => {
                return {
                    id: employee.id,
                    item: employee,
                    label: employee.name,
                    isSelected: false,
                };
            });
        const {confirmed, payload: selectedCashier} = await this.showPopup(
            "SelectionPopup",
            {
                title: this.env._t("Select Cashier"),
                list: employeesList,
            }
        );
        if (confirmed) {
            if (!this.props.line) {
                this.env.pos
                    .getOrder()
                    .getOrderlines()
                    .forEach(function (orderline) {
                        orderline.setCashier(selectedCashier);
                    });
            } else {
                this.props.line.setCashier(selectedCashier);
            }
        }
    },
    getCashier(cashier) {
        return this.cashier;
    },
    removecashier() {
        const selectedOrderline = this.env.services.pos.getOrder().getSelectedOrderline();
        if (selectedOrderline) {
            selectedOrderline.orderline_cashier = ''
        }
    }
})
return Orderline;
