/** @odoo-module **/

import { onWillStart } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { ActionMenus } from "@web/search/action_menus/action_menus";
import { refreshAacRules, aacHiddenReportIds, extractActionId } from "./aac_session_utils";

patch(ActionMenus.prototype, {
    setup() {
        super.setup(...arguments);
        const orm = useService("orm");
        onWillStart(async () => {
            await refreshAacRules(orm);
        });
    },
    async loadAvailablePrintItems() {
        const items = await super.loadAvailablePrintItems();
        const hidden = aacHiddenReportIds(this.props.resModel);
        if (!hidden.length) {
            return items;
        }
        const hid = new Set(hidden);
        return items.filter((it) => {
            const id = extractActionId(it);
            return !(id && hid.has(id));
        });
    },
});
