/** @odoo-module **/

import { BinaryField } from "@web/views/fields/binary/binary_field";
import { binaryField } from "@web/views/fields/binary/binary_field";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { PdfViewerDialog } from "./pdfViewer";
import { url } from "@web/core/utils/urls";

export class PDFBinaryField extends BinaryField {
    static template = "pdf_split_and_merge.PDFBinaryField";

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

    onFileOpen() {
        this.dialogService.add(PdfViewerDialog, {'url': this.url, 'name': this.props.name, 'close': () => this.dialogService.close()});
    }

}

export const pdfBinaryField = {
    ...binaryField,
    component: PDFBinaryField,
};

registry.category("fields").add("pdf_binary", pdfBinaryField);
