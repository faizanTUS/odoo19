/** @odoo-module **/

import { onWillStart } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { ListController } from "@web/views/list/list_controller";
import {
    aacHiddenSidebarActionIds,
    aacModelUi,
    refreshAacRules,
    extractActionId,
} from "./aac_session_utils";

patch(ListController.prototype, {
    setup() {
        super.setup(...arguments);
        const orm = useService("orm");
        onWillStart(async () => {
            await refreshAacRules(orm);
        });
    },
    getStaticActionMenuItems() {
        const items = super.getStaticActionMenuItems();
        const resModel = this.props.resModel;
        const origExport = items.export;
        if (origExport) {
            items.export = {
                ...origExport,
                isAvailable: () => {
                    const ui = aacModelUi(resModel);
                    if (ui && ui.export === false) {
                        return false;
                    }
                    return origExport.isAvailable.call(this);
                },
            };
        }
        const origDup = items.duplicate;
        if (origDup) {
            items.duplicate = {
                ...origDup,
                isAvailable: () => {
                    const ui = aacModelUi(resModel);
                    if (ui && ui.duplicate === false) {
                        return false;
                    }
                    return origDup.isAvailable.call(this);
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
        const origArchive = items.archive;
        if (origArchive) {
            items.archive = {
                ...origArchive,
                isAvailable: () => {
                    const ui = aacModelUi(resModel);
                    if (ui && ui.archive === false) {
                        return false;
                    }
                    return origArchive.isAvailable.call(this);
                },
            };
        }
        const origUnarchive = items.unarchive;
        if (origUnarchive) {
            items.unarchive = {
                ...origUnarchive,
                isAvailable: () => {
                    const ui = aacModelUi(resModel);
                    if (ui && ui.archive === false) {
                        return false;
                    }
                    return origUnarchive.isAvailable.call(this);
                },
            };
        }
        return items;
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
