/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { onMounted, useRef, useState } from "@odoo/owl";
import { SuccessfullPopuptus } from "@pos_password_reset/app/successfull_popup/successful_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";


export class ResetPopup extends AbstractAwaitablePopup {
    static template = "pos_password_reset.ResetPopup";
    static defaultProps = {
        confirmText: _t("Add"),
        cancelText: _t("Discard"),
        title: "",
        body: "",
    };

    setup() {
        super.setup();
        this.orm = useService("orm");
        this.pos = usePos();

        this.inputRef = useRef("password");
        onMounted(this.onMounted);
    }

    onMounted() {
        this.inputRef.el.focus();
    }

    onClickConfirmButton() {
        this.Confirm();
    }

    async Confirm() {
    var pass = this.inputRef.el.value;
    var employeeId =  parseInt(this.props.currentId);



        await this.orm.write("hr.employee", [employeeId], { pin: pass || '' });
        for (let i = 0; i < this.env.services.pos.employees.length; i++) {
        const user = this.env.services.pos.employees[i];
        const hashedPassword = Sha1.hash(pass);
        user.pin = hashedPassword;
    }

    await this.env.services.popup.add(SuccessfullPopuptus, {});
    this.confirm();
}
}


