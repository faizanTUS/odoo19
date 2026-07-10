/** @odoo-module **/

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";
import { Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";


export class FixDiscountButton extends Component {
    static template = "pos_orderline_fix_amount_discount.FixDiscountButton";

    setup() {
        super.setup();
        this.pos = usePos();
        this.popup = useService("popup");
    }
    async click() {
        var self = this;
        const order = this.pos.get_order();
        const line = this.pos.get_order().get_selected_orderline();
        const { confirmed, payload } = await this.popup.add(NumberPopup, {
            title: _t("Discount Amount"),
            startingValue: 0,
            isInputSelected: true,
        });
        if (confirmed && payload) {
            line.set_discount_amount(Math.min(parseFloat(line.get_price_with_tax()), parseFloat(payload)))
        }
    }
}

ProductScreen.addControlButton({
    component: FixDiscountButton,
    condition: function () {
        return this.pos.config.fix_discount;
    },
});
