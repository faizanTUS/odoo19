/** @odoo-module */

import { useState, onWillStart, onWillUpdateProps } from "@odoo/owl";
import { CogMenu } from "@web/search/cog_menu/cog_menu";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

const GROUP_XML_ID = "print_action_buttons_access.group_show_print_action_buttons";

// Store original method before patching
const originalRegistryItems = CogMenu.prototype._registryItems;

patch(CogMenu.prototype, {
    setup() {
        this.canShowButtons = useState({ value: false });
        this.user = useService("user");

        super.setup(...arguments);

        // Ensure actionItems is initialized
        if (!this.actionItems) {
            this.actionItems = [];
        }

        onWillStart(async () => {
            const hasAccess = await this.user.hasGroup(GROUP_XML_ID);
            this.canShowButtons.value = hasAccess;

            // Reload registryItems based on access
            this.registryItems = hasAccess
                ? await originalRegistryItems.call(this)
                : [];
        });

        onWillUpdateProps(async () => {
            const hasAccess = await this.user.hasGroup(GROUP_XML_ID);
            this.canShowButtons.value = hasAccess;

            // Reload registryItems based on access
            this.registryItems = hasAccess
                ? await originalRegistryItems.call(this)
                : [];
        });
    },

    get hasItems() {
        if (!this.canShowButtons.value) {
            return false;
        }
        const actionItems = Array.isArray(this.actionItems) ? this.actionItems : [];
        const registryItems = Array.isArray(this.registryItems) ? this.registryItems : [];
        return actionItems.length + registryItems.length > 0 || (this.props.items?.print?.length || 0) > 0;
    },

    async _registryItems() {
        if (!this.canShowButtons.value) {
            return [];
        }
        return originalRegistryItems.call(this);
    },

    get cogItems() {
        if (!this.canShowButtons.value) {
            return [];
        }
        const actionItems = Array.isArray(this.actionItems) ? this.actionItems : [];
        const registryItems = Array.isArray(this.registryItems) ? this.registryItems : [];
        return [...actionItems, ...registryItems].sort((item1, item2) => {
            const grp = (item1.groupNumber || 0) - (item2.groupNumber || 0);
            if (grp !== 0) {
                return grp;
            }
            return (item1.sequence || 0) - (item2.sequence || 0);
        });
    },
});