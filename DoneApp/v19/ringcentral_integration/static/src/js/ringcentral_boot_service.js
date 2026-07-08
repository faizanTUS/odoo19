/** @odoo-module **/

import { registry } from "@web/core/registry";

export const ringcentralBootService = {
    dependencies: ["ringcentral.access"],
    async start(_env, { "ringcentral.access": accessService }) {
        // Refresh access flags early; defer loading the embeddable adapter until
        // the user opens the systray widget so cross-origin iframes are not
        // injected on every backend page load.
        await accessService.refresh();
        return {};
    },
};

registry.category("services").add("ringcentral.boot", ringcentralBootService);
