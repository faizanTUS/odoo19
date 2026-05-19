/** @odoo-module **/

import { importRecordsItem } from "@base_import/import_records/import_records";
import { aacModelUi } from "./aac_session_utils";

const _origIsDisplayed = importRecordsItem.isDisplayed;
importRecordsItem.isDisplayed = async (env) => {
    const ok = await _origIsDisplayed(env);
    if (!ok) {
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
