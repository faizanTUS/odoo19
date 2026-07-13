/* @odoo-module */

import { url } from "@web/core/utils/urls";
import { _t } from "@web/core/l10n/translation";
import { App } from "@odoo/owl";
import { MessagingMenu } from "@mail/core/public_web/messaging_menu"

import { getTemplate } from "@web/core/templates";
import { registry } from "@web/core/registry";
import { session } from "@web/session";

export const PortalchatService = {
    dependencies: ["mail.store"],

    start(env) {
        if(!session.is_public){
            const app = new App(MessagingMenu, {
                env,
                getTemplate,
                translatableAttributes: ["data-tooltip"],
                translateFn: _t,
                dev: env.debug,
            })
            app.mount(document.getElementById('o_main_nav'));
            var targetElement = $('.o_header_mobile_buttons_wrap').find('.o_not_editable')[0]
//            console.log("targetElement", targetElement)
            const container = document.createElement('div');
//            console.log("container", container)
            if(targetElement){
                targetElement.parentNode.insertBefore(container, targetElement);
                app.mount(container);
            }
        }
    },

};
registry.category("services").add("website_portal_chat.portal_chat", PortalchatService);
