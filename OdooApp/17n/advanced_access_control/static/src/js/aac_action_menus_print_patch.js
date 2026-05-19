/** @odoo-module **/

import { onWillStart } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { ActionMenus } from "@web/search/action_menus/action_menus";
import {
    refreshAacRules,
    ensureAacRules,
    aacHiddenReportIds,
    aacHiddenSidebarActionIds,
    extractActionId
} from "./aac_session_utils";

patch(ActionMenus.prototype, {
    setup() {
        super.setup(...arguments);
        const orm = useService("orm");
        onWillStart(async () => {
            await refreshAacRules(orm);
        });
    },

    /**
     * Odoo 17: Reports are gathered via this getter.
     */
    get printItems() {
        const items = super.printItems;
        const hidden = aacHiddenReportIds(this.props.resModel);
        if (!hidden.length || !items) {
            return items;
        }
        const hid = new Set(hidden);
        return items.filter((it) => {
            const id = extractActionId(it);
            return !(id && hid.has(id));
        });
    },

    /**
     * Odoo 18: Reports are gathered via this async hook.
     */
    async loadAvailablePrintItems() {
        if (!super.loadAvailablePrintItems) {
            return undefined;
        }
        await ensureAacRules(this.orm);
        const items = await super.loadAvailablePrintItems();
        const hidden = aacHiddenReportIds(this.props.resModel);
        if (!hidden.length || !items) {
            return items;
        }
        const hid = new Set(hidden);
        return items.filter((it) => {
            const id = extractActionId(it);
            return !(id && hid.has(id));
        });
    },

    /**
     * Odoo 17 & 18: Sidebar actions are gathered via this method.
     */
    async getActionItems(props) {
        await ensureAacRules(this.orm);
        const items = await super.getActionItems(props);
        const hidden = aacHiddenSidebarActionIds(props.resModel);
        if (!hidden.length || !items) {
            return items;
        }
        const hid = new Set(hidden);
        return items.filter((it) => {
            const id = extractActionId(it);
            return !(id && hid.has(id));
        });
    }
});
