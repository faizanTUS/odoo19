/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { patch } from "@web/core/utils/patch";
import { ResetPopup } from "@pos_password_reset/app/reset_popup/reset_password";

patch(SelectionPopup.prototype, {
    async resetPassword(ev) {
        var currentId = ev.currentTarget.id;
//        console.log("--------reset button-------", this.env.services.pos.employees);
        ev.preventDefault();
        ev.stopPropagation();
        await this.env.services.popup.add(ResetPopup, { 'currentId': currentId });

    },
});
