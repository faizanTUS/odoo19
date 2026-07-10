import { _t } from "@web/core/l10n/translation";
import { onMounted, useRef, useState, Component } from "@odoo/owl";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { Dialog } from "@web/core/dialog/dialog";
import { useService } from "@web/core/utils/hooks";

export class PromoCodePopups extends Component {
    static template = "tus_pos_partial_giftcard.PromoCodePopups";
    static components = { Dialog };

    static props = {
        title: { type: String, optional: true },
        placeholder: { type: String, optional: true },
        partner_id: { type: String, optional: true },
        code: { type: String, optional: true },
        points: { type: Number, optional: true },
        getPayload: Function,
        close: Function,
    };
    static defaultProps = {
        confirmText: _t("Redeem"),
        cancelText: _t("Discard"),
        confirmKey: _t("Enter"),
        title: _t("Redeem Amount"),
        startingValue: "",
        points: 1,
        code: '',
        placeholder: _t("Enter amount to Redeem"),
    };
    setup() {
        super.setup();
        this.dialog = useService("dialog");
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
            this.dialog.add(AlertDialog, {
                title: _t("Error"),
                body: _t("You have not enough amount to redeem."),
            });
            return false;
        } else {
            this.props.getPayload({ confirmed: true, amount: this.RedemptionInputRef.el.value });
            this.props.close()
        }
    }
    async _onClickCancel(ev) {
        this.props.close();
    }
};
