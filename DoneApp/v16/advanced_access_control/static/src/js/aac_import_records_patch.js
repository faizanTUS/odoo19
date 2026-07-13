/** @odoo-module **/

import { importRecordsItem } from "@base_import/import_records/import_records";
import { aacModelUi, aacRules } from "./aac_session_utils";

const _origIsDisplayed = importRecordsItem.isDisplayed;
// NOTE: favoriteMenuRegistry calls isDisplayed synchronously in Odoo 16.
// Returning a Promise here would always be truthy and would break hiding.
importRecordsItem.isDisplayed = (env) => {
    const ok = _origIsDisplayed(env);
    if (!ok) {
        return false;
    }
    const rules = aacRules();
    if (!rules.empty && rules.global_disable_import) {
        return false;
    }
    const resModel = env.searchModel?.resModel;
    if (!resModel) {
        return true;
    }
    const ui = aacModelUi(resModel);
    if (ui && ui.import === false) {
        return false;
    }
    return true;
};
