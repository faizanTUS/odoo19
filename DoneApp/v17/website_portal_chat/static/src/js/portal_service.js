/* @odoo-module */

import { url } from "@web/core/utils/urls";
import { PortalchatButton } from "./portal_chat_button";
import { _t } from "@web/core/l10n/translation";
import { App } from "@odoo/owl";

import { templates } from "@web/core/assets";
import { registry } from "@web/core/registry";

//registry.category("main_components").remove("mail.ChatWindowContainer");
export const PortalchatService = {
    dependencies: ["mail.messaging", "discuss.core.common"],

    start(env) {
         if (env.services.user?.context?.uid) {
            env.services["mail.messaging"].isReady.then(() => {
                if (!env.services["mail.store"].initBusId) {
                    env.services.rpc("/mail/init_messaging", {
                        context: env.services.user.context
                    }, { silent: true }).then((data) => {
                        env.services["mail.messaging"].initMessagingCallback(data);
                        if (data.channels) {
                            for (const channelData of data.channels) {
                                env.services["discuss.core.common"].insertInitChannel(channelData);
                            }
                        }
                    });
                }
            });
        }

        const app = new App(PortalchatButton, {
            env,
            templates,
            translatableAttributes: ["data-tooltip"],
            translateFn: _t,
            dev: env.debug,
        })
        app.mount(document.getElementById('o_main_nav'));
        var targetElement = $('.o_header_mobile_buttons_wrap').find('.o_not_editable')[0]
        const container = document.createElement('div');
        if(targetElement){
            targetElement.parentNode.insertBefore(container, targetElement);
            app.mount(container);
        }
    },
};
registry.category("services").add("website_portal_chat.portal_chat", PortalchatService);
