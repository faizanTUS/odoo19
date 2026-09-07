/** @odoo-module */

//import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { Component,onMounted, useRef, useState } from "@odoo/owl";
import { SuccessfullPopuptus } from "@pos_password_reset/app/successfull_popup/successful_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { makeAwaitable} from "@point_of_sale/app/store/make_awaitable_dialog";


//AbstractAwaitablePopup
export class ResetPopup extends Component {
    static template = "pos_password_reset.ResetPopup";
    static components = { Dialog };
//    static props = {
//        ...Component.props,
//    }
    static defaultProps = {
        ...Component.defaultProps,
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
//        why we need this below for loop. assigning same pass in all the users (strange)!.
//        var all_users = this.pos.config.models['hr.employee'].getAll()
//        for (let i = 0; i < this.pos.config.models['hr.employee'].length; i++) {
//            const user = all_users[i];
//            const hashedPassword = Sha1.hash(pass);
//            user.pin = hashedPassword;
//        }

        await this.env.services.dialog.add(SuccessfullPopuptus, {
            title: _t("Success"),
            body: _t("Password updated successfully!"),
        });
        this.confirm();
    }

    confirm() {
        this.props.close();
    }

    close() {
        this.props.close();
    }
}


