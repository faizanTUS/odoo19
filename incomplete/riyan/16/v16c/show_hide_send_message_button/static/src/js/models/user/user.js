/** @odoo-module **/
import {registerPatch} from "@mail/model/model_core";
import {attr} from "@mail/model/model_field";
registerPatch({
    name: "User",
    fields: {
        not_send_msgs_btn_in_chatter: attr(),
    },
});
