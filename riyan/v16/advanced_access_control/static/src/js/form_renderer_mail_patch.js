/** @odoo-module **/

import { onWillStart } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { FormRenderer } from "@web/views/form/form_renderer";
import { FormCompiler } from "@web/views/form/form_compiler";
import { aacRules, aacHiddenButtons, aacHiddenTabs } from "./aac_session_utils";

patch(FormRenderer.prototype, "advanced_access_control.FormRenderer", {
    setup() {
        this._super(...arguments);
        onWillStart(async () => {
            const rules = aacRules();
            if (!rules.empty && rules.hide_chatter) {
                // Add a class to the whole form to hide chatter via CSS as fallback
                document.body.classList.add("aac-hide-chatter");
            } else {
                document.body.classList.remove("aac-hide-chatter");
            }
        });
    },
    get aacHideChatter() {
        const rules = aacRules();
        return !rules.empty && rules.hide_chatter;
    },
    set aacHideChatter(val) {},
});

patch(FormCompiler.prototype, "advanced_access_control.FormCompiler", {
    compileButton(el, params) {
        // Client-side fallback: hide buttons by XML name for this model.
        // Server-side arch filtering should also remove them, but OWL views
        // can remain cached; this ensures the UI respects the policy.
        try {
            const resModel = this.env?.model?.root?.resModel || this.env?.model?.resModel;
            const name = (el.getAttribute("name") || "").trim();
            if (resModel && name) {
                const hidden = new Set(aacHiddenButtons(resModel));
                if (hidden.has(name)) {
                    return null;
                }
            }
        } catch {
            // fail open
        }
        return this._super(el, params);
    },

    compileNotebook(el, params) {
        // Client-side fallback: hide notebook pages by page string for this model.
        // We temporarily remove matching <page> nodes before delegating to the core compiler.
        const removed = [];
        try {
            const resModel = this.env?.model?.root?.resModel || this.env?.model?.resModel;
            if (resModel) {
                const hiddenTitles = new Set(
                    aacHiddenTabs(resModel).map((t) => (t || "").trim()).filter((t) => t)
                );
                if (hiddenTitles.size) {
                    for (const child of [...el.children]) {
                        if (child.tagName !== "page") {
                            continue;
                        }
                        const title = (child.getAttribute("string") || "").trim();
                        if (title && hiddenTitles.has(title)) {
                            removed.push({ parent: child.parentNode, node: child, next: child.nextSibling });
                            child.remove();
                        }
                    }
                }
            }
        } catch {
            // fail open
        }
        const res = this._super(el, params);
        // Restore original arch DOM for any subsequent compilers/uses.
        for (const { parent, node, next } of removed) {
            if (!parent) continue;
            parent.insertBefore(node, next || null);
        }
        return res;
    },

    compile(node, params) {
        const res = this._super(node, params);
        // Odoo 16 mail module selectors
        const selectors = [
            ".oe_chatter",
            ".o_chatter",
            ".o_ChatterContainer",
            ".o_Chatter",
            "Chatter",
            ".o_FormRenderer_chatterContainer"
        ];
        const chatterHooks = res.querySelectorAll(selectors.join(", "));
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
