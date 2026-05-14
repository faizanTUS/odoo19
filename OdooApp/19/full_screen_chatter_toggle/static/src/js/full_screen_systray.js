/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillUnmount } from "@odoo/owl";

export class FullScreenSystray extends Component {
    setup() {
        const stored = window.localStorage.getItem("full_screen_form_enabled") === "1";
        this.state = useState({
            enabled: stored,
            show: !!document.querySelector(".o_form_view"), // visible only if form exists
        });

        this._applyClass(stored);

        // Poll DOM periodically: form views mount/unmount without a single reliable hook here.
        this._intervalId = window.setInterval(() => {
            const hasForm = !!document.querySelector(".o_form_view");
            if (hasForm !== this.state.show) {
                this.state.show = hasForm;
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
        if (enabled) {
            document.body.classList.add("o_full_screen_form");
        } else {
            document.body.classList.remove("o_full_screen_form");
        }
    }

    toggleFullScreen() {
        const enabled = !this.state.enabled;
        this.state.enabled = enabled;
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
