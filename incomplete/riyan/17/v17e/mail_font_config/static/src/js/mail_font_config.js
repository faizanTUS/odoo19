/** @odoo-module **/

/**
 *
 * Odoo 17 compatibility note:
 * This file only exposes the configured default font as a CSS variable.
 */

import { session } from "@web/session";
import { registry } from "@web/core/registry";

registry.category("services").add("mail_font_config", {
    start() {
        const fontFamily = session.mail_font_family;
        if (fontFamily) {
            document.documentElement.style.setProperty("--mail-font-family", fontFamily);
        }
    },
});
