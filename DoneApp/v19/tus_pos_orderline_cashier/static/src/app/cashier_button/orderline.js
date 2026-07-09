/** @odoo-module **/

// import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { Orderline } from "@point_of_sale/app/components/orderline/orderline";
import {registry} from "@web/core/registry";
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
//                        orderline.set_cashier(selectedCashier);
                        orderline.setCashier(selectedCashier);
                    });
            } else {
//                this.props.line.set_cashier(selectedCashier);
                this.props.line.setCashier(selectedCashier);
            }
        }
    },
//    get_cashier(cashier) {
    getCashier(cashier) {
        console.log("this is cashier=============", this.cashier)
        return this.cashier;
    },
    removecashier() {
    debugger;
//        const selectedOrderline = this.env.services.pos.get_order().get_selected_orderline();
        const selectedOrderline = this.env.services.pos.getOrder().getSelectedOrderline();
        console.log("this is selectedOrderline=============", selectedOrderline)
        if (selectedOrderline) {
            selectedOrderline.orderline_cashier = ''
        }
    }
})
return Orderline;
