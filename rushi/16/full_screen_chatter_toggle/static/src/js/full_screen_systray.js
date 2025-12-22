/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillUnmount } from "@odoo/owl";

export class FullScreenSystray extends Component {
    setup() {
        console.log("[FS] FullScreenSystray.setup called");

        const stored = window.localStorage.getItem("full_screen_form_enabled") === "1";
        this.state = useState({
            enabled: stored,
            show: !!document.querySelector(".o_form_view"), // visible only if form exists
        });

        this._applyClass(stored);

        // Poll DOM every 500ms to see if a form view is on screen
        this._intervalId = window.setInterval(() => {
            const hasForm = !!document.querySelector(".o_form_view");
            if (hasForm !== this.state.show) {
                this.state.show = hasForm;
                // optional: log for debugging
                console.log("[FS] hasForm changed ->", hasForm);
            }
        }, 500);

        onWillUnmount(() => {
            if (this._intervalId) {
                window.clearInterval(this._intervalId);
                this._intervalId = null;
            }
        });
    }

    _applyClass(enabled) {
        console.log("[FS] applyClass", enabled);
        if (enabled) {
            document.body.classList.add("o_full_screen_form");
        } else {
            document.body.classList.remove("o_full_screen_form");
        }
    }

    toggleFullScreen() {
        const enabled = !this.state.enabled;
        this.state.enabled = enabled;
        console.log("[FS] toggleFullScreen", enabled);
        window.localStorage.setItem("full_screen_form_enabled", enabled ? "1" : "0");
        this._applyClass(enabled);
    }
}

FullScreenSystray.template = "full_screen_chatter_toggle.FullScreenSystray";

const systrayItem = {
    Component: FullScreenSystray,
    isDisplayed: () => true,
    sequence: 50,
};

registry.category("systray").add(
    "full_screen_chatter_toggle_systray",
    systrayItem
);
