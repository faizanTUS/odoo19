/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormRenderer } from "@web/views/form/form_renderer";
import { FormCompiler } from "@web/views/form/form_compiler";
import { aacRules } from "./aac_session_utils";

patch(FormRenderer.prototype, {
    /**
     * Odoo 18 chatter layout hook. Returning "NONE" successfully hides the chatter.
     */
    mailLayout(hasAttachmentContainer) {
        const rules = aacRules();
        if (!rules.empty && rules.hide_chatter) {
            return "NONE";
        }
        return super.mailLayout ? super.mailLayout(hasAttachmentContainer) : undefined;
    },

    /**
     * Odoo 17 helper for template t-if (see FormCompiler patch below).
     */
    get aacHideChatter() {
        const rules = aacRules();
        return !rules.empty && rules.hide_chatter;
    }
});

patch(FormCompiler.prototype, {
    /**
     * Odoo 17: Inject hide logic into compiled template.
     * In Odoo 17, mail's patch to FormCompiler appends the chatter elements to the result.
     * By patching compile, we can find those elements and add a t-if condition.
     */
    compile(node, params) {
        const res = super.compile(node, params);
        // Find chatter containers (including those inside sheet-bg or aside)
        const chatterHooks = res.querySelectorAll(".o-mail-Form-chatter");
        for (const hook of chatterHooks) {
            const currentTIf = hook.getAttribute("t-if");
            if (currentTIf) {
                hook.setAttribute("t-if", `(${currentTIf}) and !__comp__.aacHideChatter`);
            } else {
                hook.setAttribute("t-if", "!__comp__.aacHideChatter");
            }
        }
        return res;
    }
});
