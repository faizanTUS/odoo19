/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Composer } from "@mail/components/composer/composer";

patch(Composer.prototype, "QuickChatterNotesPatch", {

    async openQuickNotes() {

    try {
        const rpc = this.env.services.rpc;

        const notes = await rpc("/quick_chatter_notes/fetch", {}) || [];

        if (!notes.length) {
            this.env.services.notification.add("No quick notes configured", { type: "info" });
            return;
        }

        const listText = notes.map((n, i) => `${i + 1}. ${n.name}`).join("\n");
        const choice = window.prompt(`Select a quick note:\n${listText}`);
        const idx = parseInt(choice, 10);
        if (!idx || idx < 1 || idx > notes.length) return;

        const content = notes[idx - 1].content || "";

        const textarea = document.querySelector('.o_ComposerTextInput_textarea');
        if (textarea) {
            const previous = textarea.value || "";
            textarea.value = previous + "\n" + content;

            textarea.dispatchEvent(new Event('input', { bubbles: true }));
            textarea.dispatchEvent(new Event('change', { bubbles: true }));

            return;
        }
    } catch (error) {
        this.env.services.notification.add("Error while loading quick notes", {
            type: "danger",
        });
    }
}
});
