/** @odoo-module **/

import { BinaryField } from "@web/views/fields/binary/binary_field";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { PdfViewerDialog } from "@pdf_split_and_merge/fields/pdfViewer";
import { url } from "@web/core/utils/urls";

export class PDFBinaryField extends BinaryField {

    setup() {
        super.setup();
        this.dialogService = useService("dialog");
    }

    get url() {
        if (!this.props.record.data[this.props.name]) {
            return null;
        }
        const page = this.props.record.data[`${this.props.name}_page`] || 1;
        const file = encodeURIComponent(
            url("/web/content", {
                model: this.props.record.resModel,
                field: this.props.name,
                id: this.props.record.resId,
            })
        );
        return `/web/static/lib/pdfjs/web/viewer.html?file=${file}#page=${page}`;
    }

    onFileOpen(ev) {
        ev.preventDefault();
        this.dialogService.add(PdfViewerDialog, {'url': this.url, 'name': this.props.name, 'close': () => this.dialogService.close()});
    }

}

PDFBinaryField.template = "pdf_split_and_merge.PDFBinaryField";

registry.category("fields").add("pdf_binary", PDFBinaryField);
