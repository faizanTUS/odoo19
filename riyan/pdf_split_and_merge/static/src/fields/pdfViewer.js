/** @odoo-module **/

import { Dialog } from "@web/core/dialog/dialog";
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class PdfViewerDialog extends Component {
    static template = "pdf_split_and_merge.PdfViewerDialog";
    static components = { Dialog };
    static props = {
        url: { type: String, optional: true},
        name: { type: String, optional: true},
        close: Function
    };

    setup() {
        super.setup();
        this.notification = useService("notification");
    }

    onLoadFailed() {
        this.notification.add(this.env._t("Could not display the selected pdf"), {
            type: "danger",
        });
    }

}
