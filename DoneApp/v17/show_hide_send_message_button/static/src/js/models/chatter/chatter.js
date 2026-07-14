/** @odoo-module */

import {ThreadService} from "@mail/core/common/thread_service";
import {parseEmail} from "@mail/js/utils";

import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";

patch(ThreadService.prototype, {
    async fetchData(
        thread,
        requestList = [
            "activities",
            "followers",
            "attachments",
            "messages",
            "suggestedRecipients",
        ]
    ) {
        const res = await super.fetchData(...arguments);
        var lst = res["not_send_msgs_btn_in_chatter"].filter((r) => r == thread.model);
        if (lst.length > 0) {
            thread["DisableSendMessageBtn"] = false;
        } else {
            thread["DisableSendMessageBtn"] = true;
        }
        return res;
    },
});
