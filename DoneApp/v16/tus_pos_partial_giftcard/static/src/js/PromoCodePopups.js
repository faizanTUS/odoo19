/** @odoo-module **/
import AbstractAwaitablePopup from "point_of_sale.AbstractAwaitablePopup";
import Registries from "point_of_sale.Registries";

const {useRef} = owl;

export default class PromoCodePopups extends AbstractAwaitablePopup {
    setup() {
        this.RedemptionInputRef = useRef("RedemptionInputRef");
    }
    async _OnClickLoad(ev) {
        let amount = document.getElementById("RedemptionInputext").value;
        if (!(this.props.points >= parseInt(amount))) {
            await this.showPopup("ErrorPopup", {
                title: this.env._t("Error"),
                body: this.env._t("You have not enough amount to redeem"),
            });
            return false;
        } else {
            this.env.posbus.trigger("close-popup", {
                popupId: this.props.id,
                response: {
                    confirmed: true,
                    amount: this.RedemptionInputRef.el.value,
                },
            });
        }
    }
    _OnClickCancel(ev) {
        this.cancel();
    }
}
PromoCodePopups.template = "PromoCodePopups";
PromoCodePopups.defaultProps = {};

Registries.Component.add(PromoCodePopups);
