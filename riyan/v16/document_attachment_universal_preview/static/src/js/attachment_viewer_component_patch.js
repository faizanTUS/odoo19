/** @odoo-module **/

import { AttachmentViewer } from "@mail/components/attachment_viewer/attachment_viewer";
import { patch } from "@web/core/utils/patch";

patch(AttachmentViewer.prototype, "document_attachment_uap_attachment_viewer", {
    _onKeydown(ev) {
        if (this.attachmentViewer.attachmentViewerViewable?.isMsOffice) {
            switch (ev.key) {
                case "+":
                case "=":
                    this.attachmentViewer.officeZoomIn();
                    ev.stopPropagation();
                    return;
                case "-":
                case "_":
                    this.attachmentViewer.officeZoomOut();
                    ev.stopPropagation();
                    return;
                case "0":
                    this.attachmentViewer.officeResetZoom();
                    ev.stopPropagation();
                    return;
            }
        }
        this._super(ev);
    },
});
