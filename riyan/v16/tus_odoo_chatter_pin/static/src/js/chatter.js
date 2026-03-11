/** @odoo-module **/

import { Chatter } from "@mail/components/chatter/chatter";
import { patch } from "@web/core/utils/patch";
import { useState, onMounted, useEnv } from "@odoo/owl";

patch(Chatter.prototype, "tus_odoo_chatter_pin.Chatter", {

    setup() {
        this._super(...arguments);

        this.pinState = useState({
            showPinnedMessages: false,
            pinnedMessages: [],
        });

        onMounted(() => {
            this._loadPinnedMessages();

            this._onPinChanged = () => {
                this._loadPinnedMessages();
            };
            document.addEventListener("tus_pin_changed", this._onPinChanged);
        });
    },

    async _loadPinnedMessages() {
        try {
            let resId = null;
            let resModel = null;

            if (this.thread) {
                resId = this.thread.id;
                resModel = this.thread.model;
            }
            if (!resId && this.props) {
                resId = this.props.resId || this.props.res_id ||
                        this.props.threadId || this.props.thread_id;
                resModel = this.props.resModel || this.props.res_model ||
                           this.props.threadModel || this.props.thread_model;
            }

            if (!resId) {
                const match = window.location.hash.match(/id=(\d+)/);
                if (match) resId = parseInt(match[1]);
            }
            if (!resModel) {
                const formView = document.querySelector(".o_form_view");
                if (formView) resModel = formView.dataset.model || formView.getAttribute("data-model");
            }


            if (!resId || !resModel) {
                return;
            }

            const result = await this.env.services.orm.call(
                "mail.message",
                "get_pinned_messages_data",
                [resId, resModel],
                {}
            );
            this.pinState.pinnedMessages = result || [];

        } catch (e) {
            console.error("[TUS Pin] _loadPinnedMessages error:", e);
        }
    },

    get pinnedMessages() {
        return this.pinState.pinnedMessages || [];
    },

    togglePinnedMessages() {
        this.pinState.showPinnedMessages = !this.pinState.showPinnedMessages;
    },

    jumpToMessage(messageId) {
        const el = document.querySelector(`.o_Message[data-message-id="${messageId}"]`);
        if (el) {
            el.scrollIntoView({ behavior: "smooth", block: "center" });
            el.classList.add("o_pinned_message_highlight");
            setTimeout(() => el.classList.remove("o_pinned_message_highlight"), 2200);
        }
    },

    async unpinMessage(message) {
        try {
            await this.env.services.orm.call(
                "mail.message",
                "toggle_pin_chatter",
                [message.id]
            );
            await this._loadPinnedMessages();
        } catch (e) {
            console.error("[TUS Pin] unpinMessage error:", e);
        }
    },
});