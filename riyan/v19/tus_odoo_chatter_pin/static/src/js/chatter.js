/** @odoo-module **/
import { Chatter } from "@mail/chatter/web_portal/chatter";
import { patch } from "@web/core/utils/patch";
import { MessageCardList } from "@mail/core/common/message_card_list";

patch(Chatter.prototype, {
    setup() {
        super.setup();
        Object.assign(this.state, {
            showPinnedMessages: false,
        });
    },

    get pinnedMessages() {
        return this.state.thread?.messages?.filter((msg) => msg.pinned_at) ?? [];
    },

    togglePinnedMessages() {
        this.state.showPinnedMessages = !this.state.showPinnedMessages;
    },
});

Object.assign(Chatter.components, { MessageCardList });
