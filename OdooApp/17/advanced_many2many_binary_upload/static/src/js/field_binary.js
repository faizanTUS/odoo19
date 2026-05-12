/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { FileInput } from "@web/core/file_input/file_input";
import { useX2ManyCrud } from "@web/views/fields/relational_utils";
import { Component, onMounted } from "@odoo/owl";

export class Many2ManyBinaryFieldDragAndDrop extends Component {
    static template = "web.Many2ManyBinaryField";
    static components = { FileInput };
    static props = {
        ...standardFieldProps,
        acceptedFileExtensions: { type: String, optional: true },
        className: { type: String, optional: true },
        numberOfFiles: { type: Number, optional: true },
    };

    setup() {
        this.notification = useService("notification");
        this.operations = useX2ManyCrud(() => this.props.record.data[this.props.name], true);

        onMounted(() => {
            const root = this.__owl__.bdom?.el;
            if (!root) {
                return;
            }
            root.addEventListener("drop", (ev) => this._onDrop(ev));
            root.addEventListener("dragenter", this._preventDefaults);
            root.addEventListener("dragover", this._preventDefaults);
            root.addEventListener("dragleave", this._preventDefaults);
        });
    }

    _preventDefaults(e) {
        e.preventDefault();
    }

    _onDrop(ev) {
        ev.preventDefault();
        const files = [];
        if (ev.dataTransfer?.items) {
            for (const item of ev.dataTransfer.items) {
                if (item.kind === "file") {
                    const file = item.getAsFile();
                    if (file) {
                        files.push(file);
                    }
                }
            }
        } else if (ev.dataTransfer?.files) {
            for (const file of ev.dataTransfer.files) {
                files.push(file);
            }
        }
        if (files.length) {
            this._triggerFileInput(files);
        }
    }

    _triggerFileInput(files) {
        const root = this.__owl__.bdom?.el;
        if (!root) {
            this.notification.add(_t("Attachment area not found."), { type: "danger" });
            return;
        }
        const wrapper = root.querySelector(".oe_add");
        if (!wrapper) {
            this.notification.add(_t("Attachment area not found."), { type: "danger" });
            return;
        }
        const input = wrapper.querySelector('input[type="file"]');
        if (!input) {
            this.notification.add(_t("File input not found."), { type: "danger" });
            return;
        }
        const dt = new DataTransfer();
        files.forEach((f) => dt.items.add(f));
        input.files = dt.files;
        input.dispatchEvent(new Event("change", { bubbles: true }));
    }

    get uploadText() {
        return this.props.record.fields[this.props.name].string;
    }

    get files() {
        return this.props.record.data[this.props.name].records.map((record) => ({
            ...record.data,
            id: record.resId,
        }));
    }

    getUrl(id) {
        return "/web/content/" + id + "?download=true";
    }

    getExtension(file) {
        return file.name.replace(/^.*\./, "");
    }

    async onFileUploaded(files) {
        for (const file of files) {
            if (file.error) {
                this.notification.add(file.error, { title: _t("Uploading error"), type: "danger" });
                return;
            }
            await this.operations.saveRecord([file.id]);
        }
    }

    async onFileRemove(deleteId) {
        const record = this.props.record.data[this.props.name].records.find(
            (rec) => rec.resId === deleteId
        );
        if (record) {
            this.operations.removeRecord(record);
        }
    }
}

export const many2ManyBinaryFieldDragAndDrop = {
    component: Many2ManyBinaryFieldDragAndDrop,
    supportedOptions: [
        {
            label: _t("Accepted file extensions"),
            name: "accepted_file_extensions",
            type: "string",
        },
        {
            label: _t("Number of files"),
            name: "number_of_files",
            type: "integer",
        },
    ],
    supportedTypes: ["many2many"],
    isEmpty: () => false,
    relatedFields: [
        { name: "name", type: "char" },
        { name: "mimetype", type: "char" },
    ],
    extractProps: ({ attrs, options }) => ({
        acceptedFileExtensions: options.accepted_file_extensions,
        className: attrs.class,
        numberOfFiles: options.number_of_files,
    }),
};

registry.category("fields").add("many2many_binary_drag_and_drop", many2ManyBinaryFieldDragAndDrop);
