/** @odoo-module */

import { useState, onWillStart, onWillUpdateProps } from "@odoo/owl";
import { ActionMenus } from "@web/search/action_menus/action_menus";
import { patch } from "@web/core/utils/patch";
import { user } from "@web/core/user";

const GROUP_XML_ID = "print_action_buttons_access.group_show_print_action_buttons";

// Store original method before patching
const originalGetActionItems = ActionMenus.prototype.getActionItems;

patch(ActionMenus.prototype, {
    setup() {
        this.canShowButtons = useState({ value: false });

        super.setup(...arguments);

        onWillStart(async () => {
            const hasAccess = await user.hasGroup(GROUP_XML_ID);
            this.canShowButtons.value = hasAccess;

            // Only modify props.items.print when access is DENIED
            if (this.props.items) {
                if (!hasAccess) {
                    // Store original print items before clearing
                    if (!this._originalPrintItems && this.props.items.print) {
                        this._originalPrintItems = [...this.props.items.print];
                    }
                    // Clear print items to hide print button
                    this.props.items.print = [];
                }
                // If hasAccess is true, leave props.items.print as is (don't modify)
            }

            // Always reload items based on access
            if (hasAccess) {
                this.actionItems = await originalGetActionItems.call(this, this.props);
            } else {
                this.actionItems = [];
            }
        });

        onWillUpdateProps(async (nextProps) => {
            const hasAccess = await user.hasGroup(GROUP_XML_ID);
            this.canShowButtons.value = hasAccess;

            // Only modify props.items.print when access is DENIED
            if (nextProps.items) {
                if (!hasAccess) {
                    // Store original print items before clearing (if not already stored)
                    if (!this._originalPrintItems && nextProps.items.print) {
                        this._originalPrintItems = [...nextProps.items.print];
                    }
                    // Clear print items to hide print button
                    nextProps.items.print = [];
                } else {
                    // If access is granted, restore original items if they were stored
                    if (this._originalPrintItems) {
                        nextProps.items.print = this._originalPrintItems;
                        // Clear the stored items after restoring
                        this._originalPrintItems = null;
                    }
                    // If _originalPrintItems doesn't exist, props.items.print is already correct
                }
            }

            // Always reload items based on access
            if (hasAccess) {
                this.actionItems = await originalGetActionItems.call(this, nextProps);
            } else {
                this.actionItems = [];
            }
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