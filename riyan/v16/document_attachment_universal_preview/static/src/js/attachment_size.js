/** @odoo-module **/

import { registry } from "@web/core/registry";
import { registerPatch } from '@mail/model/model_core';

const fieldRegistry = registry.category("fields");

// Patch the many2many_binary field definition to also fetch file_size
let originalDefinition = null;
try {
    originalDefinition = fieldRegistry.get("many2many_binary");
} catch (e) {
    // Field not present in this Odoo version; ignore the patch
}
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
try {
    const mailComposerDef = fieldRegistry.get("mail_composer_attachment_list");
    if (mailComposerDef) {
        fieldRegistry.add("mail_composer_attachment_list", {
            ...mailComposerDef,
            relatedFields: [
                ...(mailComposerDef.relatedFields || []),
                { name: "file_size", type: "integer" },
            ],
        }, { force: true });
    }
} catch (e) {
    // Field not present in this Odoo version; ignore the patch
}

// Ensure mail Attachment model keeps size/file_size when messages/attachments are loaded
try {
    registerPatch({
        name: 'Attachment',
        modelMethods: {
            convertData(data) {
                // call original convertData to get base mapping
                const base = (this._super && typeof this._super === 'function') ? this._super(data) : {};
                // copy size/file_size if available so the OWL Attachment record has it after refresh
                if ('size' in data) {
                    base.size = data.size;
                }
                if ('file_size' in data) {
                    base.file_size = data.file_size;
                    if (!('size' in base)) {
                        base.size = data.file_size;
                    }
                }
                return base;
            },
        },
    });
} catch (e) {
    // If mail.model is not present in this Odoo version, ignore
}
