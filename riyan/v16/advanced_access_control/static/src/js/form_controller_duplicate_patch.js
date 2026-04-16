/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { aacModelUi } from "./aac_session_utils";

patch(FormController.prototype, "advanced_access_control.FormControllerDuplicate", {
    getStaticActionMenuItems() {
        const items = this._super;
        const resModel = this.props.resModel;
        const { activeActions } = this.archInfo;

        const origDup = items.duplicate;
        if (origDup) {
            items.duplicate = {
                ...origDup,
                isAvailable: () => {
                    const ui = aacModelUi(resModel);
                    if (ui && ui.duplicate === false) {
                        return false;
                    }
                    return activeActions.create && activeActions.duplicate;
                },
            };
        }
        const origDel = items.delete;
        if (origDel) {
            items.delete = {
                ...origDel,
                isAvailable: () => {
                    const ui = aacModelUi(resModel);
                    if (ui && ui.unlink === false) {
                        return false;
                    }
                    return origDel.isAvailable.call(this);
                },
            };
        }
        return items;
    },
});
