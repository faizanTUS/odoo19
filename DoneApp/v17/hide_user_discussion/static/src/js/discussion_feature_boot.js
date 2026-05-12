/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { ChatWindowContainer } from "@mail/core/common/chat_window_container";
import { OutOfFocusService } from "@mail/core/common/out_of_focus_service";

if (!session.discussion_enabled) {
    const systray = registry.category("systray");
    if (systray.contains("mail.messaging_menu")) {
        systray.remove("mail.messaging_menu");
    }
}

patch(ChatWindowContainer.prototype, {
    get isDiscussionEnabled() {
        return Boolean(session.discussion_enabled);
    },
});

patch(OutOfFocusService.prototype, {
    notify() {
        if (!session.discussion_enabled) {
            return;
        }
        return super.notify(...arguments);
    },
});
