/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { useFileViewer } from "@web/core/file_viewer/file_viewer_hook";
import {
    Many2ManyBinaryField,
    many2ManyBinaryField,
} from "@web/views/fields/many2many_binary/many2many_binary_field";
import { PreviewableIrAttachment } from "./previewable_ir_attachment";

// Odoo 18: Ensure access_token is always requested for attachments in this widget
if (many2ManyBinaryField.relatedFields) {
    const fieldsToPush = [
        { name: "access_token", type: "char" },
        { name: "checksum", type: "char" },
        // Needed to display attachment size (in MB) in many2many widget and mail composer list.
        { name: "file_size", type: "integer" },
    ];
    for (const f of fieldsToPush) {
        if (!many2ManyBinaryField.relatedFields.find(rf => rf.name === f.name)) {
            many2ManyBinaryField.relatedFields.push(f);
        }
    }
}

patch(Many2ManyBinaryField.prototype, {
    setup() {
        super.setup();
        this.fileViewer = useFileViewer();
    },

    map2ToPreviewFile(file) {
        return new PreviewableIrAttachment({
            id: file.id,
            name: file.name,
            mimetype: file.mimetype,
            // Odoo core file viewer models typically use camelCase (`accessToken`),
            // but records coming from ORM use snake_case (`access_token`).
            accessToken: file.accessToken || file.access_token || file.token,
            access_token: file.access_token || file.token,
            checksum: file.checksum,
            type: file.type,
            url: file.url,
        });
    },

    map2PreviewableList() {
        return (this.files || [])
            .map((f) => this.map2ToPreviewFile(f))
            .filter((p) => p.isViewable);
    },

    map2IsPreviewable(file) {
        return this.map2ToPreviewFile(file).isViewable;
    },

    onPreviewMany2many(file) {
        const all = this.map2PreviewableList();
        const previewFile = all.find((p) => p.id === file.id);
        
        // console.log("MAP2 DEBUG - Previewing file:", previewFile);

        if (!previewFile) {
            this.notification.add(
                _t("There is no in-browser preview for this file type. Use Download instead."),
                { type: "info" }
            );
            return;
        }
        this.fileViewer.open(previewFile, all);
    },
});
