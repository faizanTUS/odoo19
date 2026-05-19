/** @odoo-module **/

import { onWillStart } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { FormController } from "@web/views/form/form_controller";
import {
    aacHiddenSidebarActionIds,
    aacHiddenReportIds,
    aacRules,
    aacModelUi,
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
    const denyArchive =
        isGlobalRO ||
        (!rules.empty && rules.global_disable_archive) ||
        (ui && ui.archive === false);
    const denyDuplicate = isGlobalRO || (ui && ui.duplicate === false);
    const denyUnlink = isGlobalRO || (ui && ui.unlink === false);

    let other = Array.isArray(base.other) ? base.other : [];
    if (denyArchive) {
        other = other.filter((it) => it.key !== "archive" && it.key !== "unarchive");
    }
    if (denyDuplicate) {
        other = other.filter((it) => it.key !== "duplicate");
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

patch(FormController.prototype, "advanced_access_control.FormController", {
    setup() {
        this._super(...arguments);
        const orm = useService("orm");
        onWillStart(async () => {
            await refreshAacRules(orm);
            const rules = aacRules();
            const ui = aacModelUi(this.props.resModel);
            if (!rules.empty && rules.global_readonly) {
                if (this.archInfo && this.archInfo.activeActions) {
                    this.archInfo.activeActions.create = false;
                    this.archInfo.activeActions.edit = false;
                    this.archInfo.activeActions.delete = false;
                    this.archInfo.activeActions.duplicate = false;
                }
            }
            if (!rules.empty && ui && this.archInfo && this.archInfo.activeActions) {
                if (ui.create === false) this.archInfo.activeActions.create = false;
                if (ui.write === false) this.archInfo.activeActions.edit = false;
                if (ui.unlink === false) this.archInfo.activeActions.delete = false;
                if (ui.duplicate === false) this.archInfo.activeActions.duplicate = false;
            }
        });
    },
    get canCreate() {
        const rules = aacRules();
        if (!rules.empty && rules.global_readonly) {
            return false;
        }
        const ui = aacModelUi(this.props.resModel);
        if (ui && ui.create === false) {
            return false;
        }
        return this._aac_canCreate !== undefined ? this._aac_canCreate : this._super;
    },
    set canCreate(val) {
        this._aac_canCreate = val;
    },

    get canEdit() {
        const rules = aacRules();
        if (!rules.empty && rules.global_readonly) {
            return false;
        }
        const ui = aacModelUi(this.props.resModel);
        if (ui && ui.write === false) {
            return false;
        }
        return this._aac_canEdit !== undefined ? this._aac_canEdit : this._super;
    },
    set canEdit(val) {
        this._aac_canEdit = val;
    },

    getActionMenuItems() {
        const base = this._super(...arguments);
        return filterActionMenus(base, this.props.resModel);
    },
});
