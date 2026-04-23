/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { useFileViewer } from "@web/core/file_viewer/file_viewer_hook";
import {
    Many2ManyBinaryField,
    many2ManyBinaryField,
} from "@web/views/fields/many2many_binary/many2many_binary_field";
import { PreviewableIrAttachment } from "./previewable_ir_attachment";

many2ManyBinaryField.relatedFields.push(
    { name: "access_token", type: "char" },
    { name: "checksum", type: "char" }
);

patch(Many2ManyBinaryField.prototype, {
    setup() {
        super.setup();
        this.fileViewer = useFileViewer();
    },

    /**
     * @param {object} file row from this.files
     */
    map2ToPreviewFile(file) {
        return new PreviewableIrAttachment({
            id: file.id,
            name: file.name,
            mimetype: file.mimetype,
            access_token: file.access_token,
            checksum: file.checksum,
        });
    },

    map2PreviewableList() {
        return this.files
            .map((f) => this.map2ToPreviewFile(f))
            .filter((p) => p.isViewable);
    },

    /**
     * @param {object} file
     */
    map2IsPreviewable(file) {
        return this.map2ToPreviewFile(file).isViewable;
    },

    /**
     * @param {object} file
     */
    onPreviewMany2many(file) {
        // Build one list and open the *same* instance that appears in it.
        // file_viewer_hook uses viewableFiles.indexOf(file) (identity); a fresh
        // PreviewableIrAttachment from map2ToPreviewFile(file) !== instance in the list.
        const all = this.map2PreviewableList();
        const previewFile = all.find((p) => p.id === file.id);
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
