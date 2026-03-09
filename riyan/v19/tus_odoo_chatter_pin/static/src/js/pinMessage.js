/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { registerMessageAction } from "@mail/core/common/message_actions";

registerMessageAction("pin_chatter", {
    condition: ({ message, thread }) => {
        // Show pin action for chatter threads only (not discuss channels which have native pin)
        return (
            thread &&
            !["discuss.channel", "mail.box"].includes(thread.model) &&
            !message.is_transient &&
            !message.isPending
        );
    },
    icon: ({ message }) =>
        message.pinned_at
            ? "fa fa-thumb-tack text-primary"
            : "fa fa-thumb-tack",
    name: ({ message }) => (message.pinned_at ? _t("Unpin") : _t("Pin")),
    onSelected: async ({ message, store }) => {
        await store.env.services.orm.call(
            "mail.message",
            "toggle_pin_chatter",
            [message.id]
        );
    },
    sequence: 15,
});
