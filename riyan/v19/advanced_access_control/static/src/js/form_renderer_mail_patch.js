/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormRenderer } from "@web/views/form/form_renderer";
import { aacRules } from "./aac_session_utils";

patch(FormRenderer.prototype, {
    mailLayout(hasAttachmentContainer) {
        const rules = aacRules();
        if (!rules.empty && rules.hide_chatter) {
            return "NONE";
        }
        return super.mailLayout(hasAttachmentContainer);
    },
});
