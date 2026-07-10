/** @odoo-module **/

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { onMounted, useRef, useState } from "@odoo/owl";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";


export class PromoCodePopups extends AbstractAwaitablePopup {
    static template = "tus_pos_partial_giftcard.PromoCodePopups";
     static defaultProps = {
        confirmText: _t("Redeem"),
        cancelText: _t("Discard"),
        confirmKey: "Enter",
        title: "Redeem Amount",
        startingValue: "",
        placeholder: "Enter amount to Redeem",
    };
    setup() {
        super.setup();
        this.state = useState({ inputValue: this.props.startingValue });
        this.RedemptionInputRef = useRef("RedemptionInputRef");
        onMounted(this.onMounted);
    }
    onMounted() {
        this.RedemptionInputRef.el.focus();
    }
    async _onClickLoad(ev) {
        let amount = this.RedemptionInputRef.el.value
        if (!(this.props.points >= parseInt(amount))) {
            await this.env.services.popup.add(ErrorPopup, {
                title: _t('Error'),
                body: _t('You have not enough amount to redeem.'),
            });
            return false;
        } else {
            this.props.close({ confirmed: true, amount: this.RedemptionInputRef.el.value })
        }
    }
    async _onClickCancel(ev) {
        this.cancel();
    }
};
