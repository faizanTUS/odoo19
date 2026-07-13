/* @odoo-module */

import { url } from "@web/core/utils/urls";
import { _t } from "@web/core/l10n/translation";
import { App } from "@odoo/owl";
import { MessagingMenu } from "@mail/core/public_web/messaging_menu";
import { getTemplate } from "@web/core/templates";
import { registry } from "@web/core/registry";
import { session } from "@web/session";

// Stub services for portal environment
if (!registry.category("services").contains("command")) {
    registry.category("services").add("command", {
        start() {
            return {
                add: () => () => { },
                openMainPalette: () => { },
            };
        },
    });
}
if (!registry.category("services").contains("title")) {
    registry.category("services").add("title", {
        start() {
            return {
                setParts: () => { },
                getParts: () => ({}),
                setCounters: () => { },
            };
        },
    });
}

export const PortalchatService = {
    dependencies: ["mail.store", "bus_service"],

    start(env) {
        if (!session.is_public) {
            const appConfig = {
                env,
                getTemplate,
                translatableAttributes: ["data-tooltip"],
                translateFn: _t,
                dev: env.debug,
            };

            // Wait for the DOM to be ready before mounting
            const mountApp = () => {
                // Try to find the container added in website_chat_menu.xml
                const desktopContainer = document.querySelector('.o-mail-DiscussSystray-class');
                if (desktopContainer) {
                    const desktopApp = new App(MessagingMenu, appConfig);
                    desktopApp.mount(desktopContainer);
                } else {
                    const navElement = document.getElementById('o_main_nav');
                    if (navElement) {
                        const container = document.createElement('div');
                        container.classList.add('o-mail-DiscussSystray-class', 'ms-2');
                        navElement.appendChild(container);
                        const desktopApp = new App(MessagingMenu, appConfig);
                        desktopApp.mount(container);
                    }
                }

                const mobileWrap = document.querySelector('.o_header_mobile_buttons_wrap');
                if (mobileWrap) {
                    const targetElement = mobileWrap.querySelector('.o_not_editable');
                    console.log("targetElement", targetElement);
                    if (targetElement) {
                        const container = document.createElement('div');
                        container.classList.add('o-mail-DiscussSystray-class');
                        targetElement.parentNode.insertBefore(container, targetElement);
                        const mobileApp = new App(MessagingMenu, appConfig);
                        mobileApp.mount(container);
                    } else {
                        // Fallback: append to the wrapper if no specific target found (e.g. empty menu)
                        const container = document.createElement('div');
                        container.classList.add('o-mail-DiscussSystray-class');
                        mobileWrap.appendChild(container); // Append to the end of the list
                        const mobileApp = new App(MessagingMenu, appConfig);
                        mobileApp.mount(container);
                    }
                }
            };

            if (document.readyState === "loading") {
                document.addEventListener("DOMContentLoaded", mountApp);
            } else {
                mountApp();
            }
        }
    },
};
registry.category("services").add("website_portal_chat.portal_chat", PortalchatService);
