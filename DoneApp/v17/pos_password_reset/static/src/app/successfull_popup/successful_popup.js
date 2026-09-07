/** @odoo-module */
import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _lt } from "@web/core/l10n/translation";

export class SuccessfullPopuptus extends AbstractAwaitablePopup {
    static template = "pos_password_reset.SuccessfullPopuptus";
    static defaultProps = {
        confirmText: _lt("Ok"),
        title: _lt("Success"),
        body: "",
    };

    async confirm() {
        super.confirm();
    }
}