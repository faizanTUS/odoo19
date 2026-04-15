/** @odoo-module **/

import { onWillStart } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import {
    aacHiddenSidebarActionIds,
    aacRules,
    refreshAacRules,
    extractActionId,
} from "./aac_session_utils";

patch(FormController.prototype, {
    setup() {
        super.setup();
        onWillStart(async () => {
            await refreshAacRules(this.orm);
            const rules = aacRules();
            if (!rules.empty && rules.global_readonly) {
                this.canCreate = false;
                this.canEdit = false;
            }
        });
    },
    get actionMenuItems() {
        const base = super.actionMenuItems;
        const resModel = this.props.resModel;
        const hidden = aacHiddenSidebarActionIds(resModel);
        if (!hidden.length) {
            return base;
        }
        const hid = new Set(hidden);
        const action = (base.action || []).filter((item) => {
            const id = extractActionId(item);
            return !(id && hid.has(id));
        });
        return { ...base, action };
    },
});
