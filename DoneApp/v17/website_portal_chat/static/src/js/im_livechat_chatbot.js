/* @odoo-module */

import { ChatBotService } from "@im_livechat/embed/common/chatbot/chatbot_service";
import { patch } from "@web/core/utils/patch";

patch(ChatBotService.prototype, {
    isChatbotThread(thread) {
        return thread?.operator?.id === this.chatbot?.partnerId;
    },
});