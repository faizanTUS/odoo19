odoo.define("tus_pos_orderline_cashier.quotations", function (require) {
    "use strict";

    var {Orderline} = require("point_of_sale.models");
    const Registries = require("point_of_sale.Registries");

    const PosOrderLineCashier = (Orderline) =>
        class PosOrderLineCashier extends Orderline {
            initialize(attr, options) {
                super.initialize(...arguments);
                this.cashier = this.cashier || "";
                this.cashier_id = this.cashier_id || 0.0;
            }

            set_cashier(cashier) {
                this.cashier = cashier.name;
                this.cashier_id = cashier.id;
            }

            get_cashier(cashier) {
                return this.cashier;
            }

            can_be_merged_with(orderline) {
                if (orderline.get_cashier() !== this.get_cashier()) {
                    return false;
                }
                    return super.can_be_merged_with(...arguments);

            }

            clone() {
                var orderline = super.clone();
                orderline.cashier = this.cashier;
                orderline.cashier_id = this.cashier_id;
                return orderline;
            }

            export_as_JSON() {
                var json = super.export_as_JSON();
                json.cashier = this.cashier;
                json.cashier_id = this.cashier_id;
                return json;
            }

            init_from_JSON(json) {
                super.init_from_JSON(...arguments);
                this.cashier = json.cashier;
                this.cashier_id = json.cashier_id;
            }

            export_for_printing() {
                var orders = super.export_for_printing();
                var new_val = {
                    cashier: this.get_cashier(),
                };
                $.extend(orders, new_val);
                return orders;
            }
        };
    Registries.Model.extend(Orderline, PosOrderLineCashier);
});
