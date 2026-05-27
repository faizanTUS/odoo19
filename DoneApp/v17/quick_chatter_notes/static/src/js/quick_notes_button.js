/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Composer } from "@mail/core/common/composer";
import { rpcService } from "@web/core/network/rpc_service";

patch(Composer.prototype, {

    /**
     * Open quick notes popup and insert selected note into composer
     */
    async openQuickNotes() {

        try {
            const rpc = this.env.services.rpc;
            const notes = await rpc("/quick_chatter_notes/fetch", {}) || [];


            if (!notes.length) {
                this.env.services.notification.add(
                    "No quick notes configured",
                    { type: "info" }
                );
                return;
            }

            const listText = notes
                .map((n, index) => `${index + 1}. ${n.name}`)
                .join("\n");

            const choice = window.prompt(
                `Select a quick note by number:\n${listText}`
            );

            const idx = parseInt(choice, 10);
            if (!idx || idx < 1 || idx > notes.length) {
                return;
            }

            const note = notes[idx - 1];

            // Locate textarea inside composer
            let textarea = this.root?.el?.querySelector("textarea.o-mail-Composer-input");

            if (!textarea) {
                textarea = document.querySelector(
                    ".o-mail-Composer textarea.o-mail-Composer-input"
                );
            }

            if (!textarea) {
                this.env.services.notification.add(
                    "Could not find chatter composer field",
                    { type: "warning" }
                );
                return;
            }

            textarea.value = textarea.value
                ? textarea.value + "\n" + note.content
                : note.content;

            textarea.dispatchEvent(new Event("input", { bubbles: true }));
            textarea.focus();

        } catch (error) {
            console.error("Quick Chatter Notes · error", error);
            this.env.services.notification.add(
                "Error while loading quick notes",
                { type: "danger" }
            );
        }
    },
});
