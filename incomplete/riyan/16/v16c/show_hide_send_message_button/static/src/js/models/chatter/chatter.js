/** @odoo-module **/

import {registerPatch} from "@mail/model/model_core";
import {attr} from "@mail/model/model_field";

//Added fields related to hide send message button
registerPatch({
    name: "Chatter",
    fields: {
        isShowSendMessage: attr({
            compute() {
                if (this.messaging && this.messaging.currentUser) {
                    var lst =
                        this.messaging.currentPartner.not_send_msgs_btn_in_chatter.filter(
                            (r) => r.model == this.threadModel
                        );
                    if (lst.length > 0) {
                        return false;
                    }
                }
                return true;
            },
        }),
    },
});
