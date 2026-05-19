/** @odoo-module */

import { useState, onWillStart, onWillUpdateProps } from "@odoo/owl";
import { ActionMenus } from "@web/search/action_menus/action_menus";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

const GROUP_XML_ID = "print_action_buttons_access.group_show_print_action_buttons";

const _originalSetup = ActionMenus.prototype.setup;

patch(ActionMenus.prototype, "print_action_buttons_access", {
    setup() {

        this._accessState = useState({ allowed: false });
        this._userSvc = useService("user");

        _originalSetup.call(this);

        const checkAccess = async () => {
            const hasAccess = await this._userSvc.hasGroup(GROUP_XML_ID);
            this._accessState.allowed = hasAccess;
        };

        onWillStart(checkAccess);
        onWillUpdateProps(checkAccess);
    },

    isAccessAllowed() {
        return this._accessState && this._accessState.allowed;
    },
});