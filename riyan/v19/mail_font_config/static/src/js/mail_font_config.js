/** @odoo-module **/

/**
 * mail_font_config.js
 *
 * Injects FontPlugin + FontFamilyPlugin into the mail Composer's Wysiwyg
 * editor so that the font-family selector appears in the chatter toolbar
 * (Send Message, Log Note) and in mail.template body editors.
 *
 * When a user selects text and picks a font family, the editor wraps the
 * selection in an inline <span style="font-family:..."> element.  Because the
 * HTML is stored with that inline style, the font is rendered correctly:
 *   • in the chatter (visible to everyone)
 *   • in the received email (email clients honour inline font-family)
 *
 * In addition a boot service reads the admin-configured default font from the
 * session and exposes it as the CSS custom property --mail-font-family so that
 * the SCSS file can apply it as the visual default inside every editable area.
 */

import { Composer } from "@mail/core/common/composer";
import { FontPlugin } from "@html_editor/main/font/font_plugin";
import { FontFamilyPlugin } from "@mail_font_config/js/font_family_plugin";
import { session } from "@web/session";
import { registry } from "@web/core/registry";

// ─── 1. Boot service: expose admin default font as CSS variable ──────────────
registry.category("services").add("mail_font_config", {
    start() {
        const fontFamily = session.mail_font_family;
        if (fontFamily) {
            document.documentElement.style.setProperty("--mail-font-family", fontFamily);
        }
    },
});

// ─── 2. Inject FontPlugin + FontFamilyPlugin into the mail Composer ──────────
//
// Composer.wysiwygConfig is a class getter. We override it with
// Object.defineProperty so we can call the original and extend the Plugins
// array without modifying Odoo core files.
//
// FontFamilyPlugin depends on "font" (FontPlugin), so both must be present.
// The editor's dependency resolver handles the rest automatically.

const _originalWysiwygDescriptor = Object.getOwnPropertyDescriptor(
    Composer.prototype,
    "wysiwygConfig"
);

Object.defineProperty(Composer.prototype, "wysiwygConfig", {
    configurable: true,
    get() {
        const config = _originalWysiwygDescriptor.get.call(this);
        if (config.Plugins && !config.Plugins.includes(FontFamilyPlugin)) {
            // Append both plugins; order matters – FontPlugin must precede FontFamilyPlugin
            config.Plugins = [...config.Plugins, FontPlugin, FontFamilyPlugin];
        }
        return config;
    },
});
