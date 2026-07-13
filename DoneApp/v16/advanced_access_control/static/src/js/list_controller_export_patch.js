/** @odoo-module **/

import { onWillStart } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { ListController } from "@web/views/list/list_controller";
import {
    aacHiddenSidebarActionIds,
    aacHiddenReportIds,
    aacModelUi,
    aacRules,
    refreshAacRules,
    extractActionId,
} from "./aac_session_utils";

function filterActionMenus(base, resModel) {
    if (!base || typeof base !== "object") {
        return base;
    }
    const rules = aacRules();
    const ui = aacModelUi(resModel);
    const isGlobalRO = !rules.empty && rules.global_readonly;
    const denyExport =
        isGlobalRO ||
        (!rules.empty && rules.global_disable_export) ||
        (ui && ui.export === false);
    const denyArchive =
        isGlobalRO ||
        (!rules.empty && rules.global_disable_archive) ||
        (ui && ui.archive === false);
    const denyUnlink = isGlobalRO || (ui && ui.unlink === false);

    let other = Array.isArray(base.other) ? base.other : [];
    if (denyExport) {
        other = other.filter((it) => it.key !== "export");
    }
    if (denyArchive) {
        other = other.filter((it) => it.key !== "archive" && it.key !== "unarchive");
    }
    if (denyUnlink) {
        other = other.filter((it) => it.key !== "delete");
    }

    // ActionMenus (OWL) items shape does not support a "relate" key in Odoo 16.
    // If some upstream code provides "relate", merge it into "action".
    const hiddenActionIds = new Set(aacHiddenSidebarActionIds(resModel) || []);
    let action = [
        ...(Array.isArray(base.action) ? base.action : []),
        ...(Array.isArray(base.relate) ? base.relate : []),
    ];
    if (hiddenActionIds.size) {
        action = action.filter((it) => {
            const id = extractActionId(it);
            return !(id && hiddenActionIds.has(id));
        });
    }

    const hiddenReportIds = new Set(aacHiddenReportIds(resModel) || []);
    let print = Array.isArray(base.print) ? base.print : [];
    if (hiddenReportIds.size) {
        print = print.filter((it) => {
            const id = extractActionId(it);
            return !(id && hiddenReportIds.has(id));
        });
    }

    // Return only the allowed shape keys.
    return { other, action, print };
}

patch(ListController.prototype, "advanced_access_control.ListController", {
    setup() {
        this._super(...arguments);
        const orm = useService("orm");
        onWillStart(async () => {
            await refreshAacRules(orm);
            const rules = aacRules();
            const ui = aacModelUi(this.props.resModel);
            if (this.archInfo && this.archInfo.activeActions && !rules.empty) {
                if (rules.global_readonly) {
                    this.archInfo.activeActions.create = false;
                    this.archInfo.activeActions.edit = false;
                    this.archInfo.activeActions.delete = false;
                }
                if (ui) {
                    if (ui.create === false) this.archInfo.activeActions.create = false;
                    if (ui.write === false) this.archInfo.activeActions.edit = false;
                    if (ui.unlink === false) this.archInfo.activeActions.delete = false;
                    if (ui.export === false) this.archInfo.activeActions.exportXlsx = false;
                }
                if (rules.global_disable_export) {
                    this.archInfo.activeActions.exportXlsx = false;
                }
            }
        });
    },
    getActionMenuItems() {
        const base = this._super(...arguments);
        return filterActionMenus(base, this.props.resModel);
    },
});
