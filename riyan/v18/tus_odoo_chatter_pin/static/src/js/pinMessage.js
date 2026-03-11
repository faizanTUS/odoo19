/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { messageActionsRegistry } from "@mail/core/common/message_actions";

messageActionsRegistry.add("pin_chatter", {

    condition: ({ message }) =>
        !message.isPending && message.message_type === "comment",

    icon: ({ message }) =>
        message.pinned_at ? "fa fa-thumb-tack text-primary" : "fa fa-thumb-tack",

    name: ({ message }) =>
        message.pinned_at ? _t("Unpin") : _t("Pin"),

    title: ({ message }) =>
        message.pinned_at ? _t("Unpin") : _t("Pin"),

    async onClick({ message, env }) {
        await env.services.orm.call(
            "mail.message",
            "toggle_pin_chatter",
            [message.id]
        );
        message.pinned_at = !message.pinned_at;
    },

    sequence: 15,
});