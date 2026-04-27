/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { ChatWindowManagerContainer } from "@mail/components/chat_window_manager_container/chat_window_manager_container";
import { registerPatch } from "@mail/model/model_core";
import { systrayService } from "@mail/services/systray_service";
import { ActivityMenuContainer } from "@mail/components/activity_menu_container/activity_menu_container";
import { CallSystrayMenuContainer } from "@mail/components/call_systray_menu_container/call_systray_menu_container";

patch(systrayService, "hide_user_discussion.systrayService", {
    start() {
        if (session.discussion_enabled) {
            return this._super(...arguments);
        }
        // Don't register the messaging systray at all when discussion is disabled.
        const systray = registry.category("systray");
        systray.add("mail.ActivityMenu", { Component: ActivityMenuContainer }, { sequence: 20 });
        systray.add("mail.CallSystrayMenuContainer", { Component: CallSystrayMenuContainer }, { sequence: 100 });
    },
});

patch(ChatWindowManagerContainer.prototype, "hide_user_discussion.ChatWindowManagerContainer", {
    get isDiscussionEnabled() {
        return Boolean(session.discussion_enabled);
    },
});

// Odoo 16: native/odoo notifications are sent via UserNotificationManager.
registerPatch({
    name: "UserNotificationManager",
    recordMethods: {
        sendNotification() {
            if (!session.discussion_enabled) {
                return;
            }
            return this._super(...arguments);
        },
    },
});
