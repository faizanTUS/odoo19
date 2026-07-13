/** @odoo-module **/

import { onWillStart } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { ActionMenus } from "@web/search/action_menus/action_menus";
import {
    refreshAacRules,
    aacRules,
} from "./aac_session_utils";

patch(ActionMenus.prototype, "advanced_access_control.ActionMenus", {
    setup() {
        this._super(...arguments);
        const orm = useService("orm");
        onWillStart(async () => {
            await refreshAacRules(orm);
            const rules = aacRules();
            const enable = !rules.empty;
            document.body.classList.toggle("aac-no-export", enable && !!rules.global_disable_export);
            document.body.classList.toggle("aac-no-archive", enable && !!rules.global_disable_archive);
            document.body.classList.toggle("aac-global-readonly", enable && !!rules.global_readonly);
        });
    },
});
