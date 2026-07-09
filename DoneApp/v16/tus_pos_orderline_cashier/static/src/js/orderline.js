odoo.define("tus_pos_orderline_cashier.orderline", function (require) {
    "use strict";

    const Orderline = require("point_of_sale.Orderline");
    const Registries = require("point_of_sale.Registries");

    const PosResOrderline = (Orderline) =>
        class extends Orderline {
            async usericonclick() {
                const employeesList = this.env.pos.employees
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
                            .get_order()
                            .get_orderlines()
                            .forEach(function (orderline) {
                                orderline.set_cashier(selectedCashier);
                            });
                    } else {
                        this.props.line.set_cashier(selectedCashier);
                    }
                }
            }
            removecashier() {
                this.props.line.cashier = "";
                this.props.line.cashier_id = "";
            }
        };

    Registries.Component.extend(Orderline, PosResOrderline);

    return Orderline;
});
