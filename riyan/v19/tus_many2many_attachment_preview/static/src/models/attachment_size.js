/** @odoo-module **/

import { registry } from "@web/core/registry";

const fieldRegistry = registry.category("fields");

// Patch the many2many_binary field definition to also fetch file_size
const originalDefinition = fieldRegistry.get("many2many_binary");
if (originalDefinition) {
    fieldRegistry.add("many2many_binary", {
        ...originalDefinition,
        relatedFields: [
            ...originalDefinition.relatedFields,
            { name: "file_size", type: "integer" },
        ],
    }, { force: true });
}

// Also patch mail_composer_attachment_list to fetch file_size in the mail wizard
const mailComposerDef = fieldRegistry.get("mail_composer_attachment_list");
if (mailComposerDef) {
    fieldRegistry.add("mail_composer_attachment_list", {
        ...mailComposerDef,
        relatedFields: [
            ...mailComposerDef.relatedFields,
            { name: "file_size", type: "integer" },
        ],
    }, { force: true });
}
