/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Composer } from "@mail/core/common/composer";
import { rpc } from "@web/core/network/rpc";

// In Odoo 18, patch signature is: patch(target, propertiesObject)
patch(Composer.prototype, {
    /**
     * Open the quick-notes chooser and append the selected note
     * into the current mail composer input.
     */
    async openQuickNotes() {

        try {
            const result = await rpc("/quick_chatter_notes/fetch", {});
            const notes = Array.isArray(result) ? result : [];

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

            // Find the textarea in the OWL mail composer.
            // Try multiple approaches to access the DOM element
            let textarea = null;

            // Approach 1: Try root.el if available (OWL component)
            if (this.root?.el) {
                textarea = this.root.el.querySelector("textarea.o-mail-Composer-input") ||
                          this.root.el.querySelector("textarea");
            }

            // Approach 2: Try document query for active composer
            if (!textarea) {
                const composerEl = document.querySelector(".o-mail-Composer:not(.o-mail-Composer--hidden)") ||
                                  document.querySelector(".o-mail-Composer");
                if (composerEl) {
                    textarea = composerEl.querySelector("textarea.o-mail-Composer-input") ||
                              composerEl.querySelector("textarea");
                }
            }

            // Approach 3: Fallback to any visible composer textarea
            if (!textarea) {
                textarea = document.querySelector("textarea.o-mail-Composer-input:not([disabled])") ||
                          document.querySelector("textarea[placeholder*='message' i]:not([disabled])");
            }

            if (!textarea) {
                console.warn("Quick Chatter Notes · composer textarea not found in DOM");
                this.env.services.notification.add(
                    "Could not find chatter composer field",
                    { type: "warning" }
                );
                return;
            }

            const current = textarea.value || "";
            textarea.value = current ? `${current}\n${note.content}` : note.content;

            // Trigger input event to notify OWL of the change
            textarea.dispatchEvent(new Event("input", { bubbles: true }));
            textarea.dispatchEvent(new Event("change", { bubbles: true }));
            textarea.focus();
        } catch (error) {
            console.error("Quick Chatter Notes · error in openQuickNotes", error);
            this.env.services.notification.add(
                "Error while loading quick notes",
                { type: "danger" }
            );
        }
    },
});
