/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { CashierSelectionPopup } from "@pos_hr/app/components/popups/cashier_selection_popup/cashier_selection_popup";
import { ResetPopup } from "@pos_password_reset/app/reset_popup/reset_password";

patch(CashierSelectionPopup.prototype, {
    async resetPassword(ev, employee) {
        ev.preventDefault();
        ev.stopPropagation();
        await this.env.services.dialog.add(ResetPopup, {
            employee,
        });
    },
});
