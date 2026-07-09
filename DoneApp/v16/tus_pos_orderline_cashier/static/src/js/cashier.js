odoo.define("tus_pos_orderline_cashier.OrderlineCashierButton", function (require) {
    "use strict";

    const PosComponent = require("point_of_sale.PosComponent");
    const ProductScreen = require("point_of_sale.ProductScreen");
    const Registries = require("point_of_sale.Registries");
    const {useListener} = require("@web/core/utils/hooks");

    class OrderlineCashierButton extends PosComponent {
        setup() {
            super.setup();
            useListener("click", this.onClick);
        }

        async onClick() {
            const selectedOrderline = this.env.pos.get_order().get_selected_orderline();
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
                selectedOrderline.set_cashier(selectedCashier);
            }
        }
    }

    OrderlineCashierButton.template = "OrderlineCashierButton";

    ProductScreen.addControlButton({
        component: OrderlineCashierButton,
        condition: function () {
            return this.env.pos.config.allow_orderline_user;
        },
    });

    Registries.Component.add(OrderlineCashierButton);

    return OrderlineCashierButton;
});
