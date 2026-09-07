/** @odoo-module */
//import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { Component } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

//import { _lt } from "@web/core/l10n/translation";
import { _t } from "@web/core/l10n/translation";

export class SuccessfullPopuptus extends Component {
    static template = "pos_password_reset.SuccessfullPopuptus";
    static components = { Dialog };
    static defaultProps = {
        confirmText: _t("Ok"),
        title: _t("Success"),
        body: "",
    };
    async confirm() {
        this.props.close();
    }
}