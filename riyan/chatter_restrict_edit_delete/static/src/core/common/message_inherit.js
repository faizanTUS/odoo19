/** @odoo-module */

import { Message } from "@mail/core/common/message";
import { patch } from "@web/core/utils/patch";
import { onWillStart } from "@odoo/owl";
import { user } from "@web/core/user";

patch(Message.prototype, {
    setup() {
        super.setup();
        onWillStart(async () => {
            this.showBtn = !(await user.hasGroup('chatter_restrict_edit_delete.chatter_restrict_edit_delete_group_user'));
        });
    },
});