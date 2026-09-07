/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { patch } from "@web/core/utils/patch";
import { ResetPopup } from "@pos_password_reset/app/reset_popup/reset_password";
import { Dialog } from "@web/core/dialog/dialog";
import { makeAwaitable} from "@point_of_sale/app/store/make_awaitable_dialog";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";
import { user } from "@web/core/user";
import { onWillStart } from "@odoo/owl";


patch(SelectionPopup.prototype, {
    setup() {
        super.setup();
//        this.isAdminUser = await user.hasGroup("base.group_system");

//        onWillStart(async () => {
////            super.onWillStart()
//            this.isAdminUser = await user.hasGroup("base.group_system");
//
//        });

    },



    async resetPassword(ev) {
        var currentId = ev.currentTarget.id;
        ev.preventDefault();
        ev.stopPropagation();
        await this.env.services.dialog.add(ResetPopup, { 'currentId': currentId, 'isAdminUser': user.hasGroup("base.group_system")});
//        const selectedCashierUser = await makeAwaitable(this.dialog, ResetPopup, {
//                    'currentId': currentId
//        });
    },

//    cust_IsAdminUser() {
//        return this.isAdminUser
//    }
});
