/** @odoo-module */

import { Message } from "@mail/core/common/message";
import { patch } from "@web/core/utils/patch";
import { onWillStart } from "@odoo/owl";

patch(Message.prototype, {
    setup() {
        super.setup();
        onWillStart(async () => {
            debugger;
            this.showBtn = !(await this.user.hasGroup('chatter_restrict_edit_delete.chatter_restrict_edit_delete_group_user'))
        })
    },
});
