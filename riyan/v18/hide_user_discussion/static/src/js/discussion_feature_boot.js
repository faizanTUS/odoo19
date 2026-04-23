/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { ChatHub } from "@mail/core/common/chat_hub";

if (!session.discussion_enabled) {
    const systray = registry.category("systray");
    if (systray.contains("mail.messaging_menu")) {
        systray.remove("mail.messaging_menu");
    }
}

patch(ChatHub.prototype, {
    get discussUiAllowed() {
        return Boolean(session.discussion_enabled);
    },
});
