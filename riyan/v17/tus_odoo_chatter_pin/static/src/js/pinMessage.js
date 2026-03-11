/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { messageActionsRegistry } from "@mail/core/common/message_actions";

messageActionsRegistry.add("pin_chatter", {

    condition: (component) => component.props.message?.id,

    icon: "fa-thumb-tack",

    title: (component) => {
        const message = component.props.message;
        return message.pinned_at ? _t("Unpin") : _t("Pin");
    },

    async onClick(component) {
        const message = component.props.message;

        await component.env.services.orm.call(
            "mail.message",
            "toggle_pin_chatter",
            [message.id]
        );

        message.pinned_at = !message.pinned_at;
    },

    sequence: 15,
});