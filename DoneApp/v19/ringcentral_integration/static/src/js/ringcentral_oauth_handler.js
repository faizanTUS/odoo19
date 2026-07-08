/** @odoo-module **/

import { registry } from "@web/core/registry";

/**
 * Handle RingCentral OAuth return query parameters and show notifications.
 */
export function setupRingCentralOAuthHandler(notification) {
    const params = new URLSearchParams(window.location.search);
    const status = params.get("ringcentral_status");
    if (!status) {
        return;
    }
    const message = params.get("ringcentral_message");
    if (status === "success") {
        notification.add("RingCentral account connected successfully.", {
            type: "success",
        });
    } else if (status === "error") {
        notification.add(message || "RingCentral connection failed.", {
            type: "danger",
        });
    }
    params.delete("ringcentral_status");
    params.delete("ringcentral_message");
    const hash = window.location.hash || "";
    const query = params.toString();
    const nextUrl = `${window.location.pathname}${query ? `?${query}` : ""}${hash}`;
    window.history.replaceState({}, document.title, nextUrl);
}

registry.category("services").add(
    "ringcentral.oauth",
    {
        dependencies: ["notification"],
        start(_env, { notification }) {
            setupRingCentralOAuthHandler(notification);
            return {};
        },
    },
    { force: true }
);
