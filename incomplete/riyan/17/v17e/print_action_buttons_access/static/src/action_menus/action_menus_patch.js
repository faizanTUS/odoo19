/** @odoo-module */

import { useState, onWillStart, onWillUpdateProps } from "@odoo/owl";
import { ActionMenus } from "@web/search/action_menus/action_menus";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

const GROUP_XML_ID = "print_action_buttons_access.group_show_print_action_buttons";

// Store original method before patching
const originalGetActionItems = ActionMenus.prototype.getActionItems;

patch(ActionMenus.prototype, {
    setup() {
        this.canShowButtons = useState({ value: false });
        this.user = useService("user");

        super.setup(...arguments);

        onWillStart(async () => {
            const hasAccess = await this.user.hasGroup(GROUP_XML_ID);
            this.canShowButtons.value = hasAccess;

            if (!hasAccess && this.props.items?.print) {
                // Store and clear print items when access is denied
                this._originalPrintItems = this.props.items.print;
                this.props.items.print = [];
            }

            // Reload actionItems based on access
            this.actionItems = hasAccess
                ? await originalGetActionItems.call(this, this.props)
                : [];
        });

        onWillUpdateProps(async (nextProps) => {
            const hasAccess = await this.user.hasGroup(GROUP_XML_ID);
            this.canShowButtons.value = hasAccess;

            if (nextProps.items) {
                if (!hasAccess) {
                    // Store and clear print items when access is denied
                    if (!this._originalPrintItems && nextProps.items.print) {
                        this._originalPrintItems = nextProps.items.print;
                    }
                    nextProps.items.print = [];
                } else if (this._originalPrintItems) {
                    // Restore print items when access is granted
                    nextProps.items.print = this._originalPrintItems;
                    this._originalPrintItems = null;
                }
            }

            // Reload actionItems based on access
            this.actionItems = hasAccess
                ? await originalGetActionItems.call(this, nextProps)
                : [];
        });
    },

    async getActionItems(props) {
        if (!this.canShowButtons.value) {
            return [];
        }
        return originalGetActionItems.call(this, props);
    },

    async loadAvailablePrintItems() {
        if (!this.canShowButtons.value) {
            return [];
        }
        return super.loadAvailablePrintItems();
    },

    async loadPrintItems() {
        if (!this.canShowButtons.value) {
            this.state.printItems = [];
            return;
        }
        return super.loadPrintItems();
    },
});