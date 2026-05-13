/** @odoo-module **/

import { registry } from "@web/core/registry";

const fieldRegistry = registry.category("fields");

function addFileSizeField(fieldName) {
    const definition = fieldRegistry.get(fieldName);
    if (!definition) {
        return;
    }
    const relatedFields = definition.relatedFields || [];
    if (relatedFields.some((field) => field.name === "file_size")) {
        return;
    }
    fieldRegistry.add(
        fieldName,
        {
            ...definition,
            relatedFields: [
                ...relatedFields,
                { name: "file_size", type: "integer" },
            ],
        },
        { force: true }
    );
}

addFileSizeField("many2many_binary");
addFileSizeField("many2many_binary_drag_and_drop");
addFileSizeField("mail_composer_attachment_list");
