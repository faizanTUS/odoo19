/** @odoo-module **/

/**
 * Odoo 16 - Patch the mail.AttachmentViewer component to render Office documents.
 *
 * In Odoo 16, the attachment viewer is `mail.AttachmentViewer` (a legacy Messaging
 * component). We patch:
 *   - The component class: add office zoom/scroll handlers + keyboard shortcuts.
 *   - The AttachmentViewerViewable model: add `isMsOffice` helper (computed from
 *     the attachment's isMsOffice field).
 */

import { registerPatch } from "@mail/model/model_core";
import { attr } from "@mail/model/model_field";
import { browser } from "@web/core/browser/browser";

// ─── Patch AttachmentViewerViewable ──────────────────────────────────────────

registerPatch({
    name: "AttachmentViewerViewable",
    fields: {
        /**
         * True when the underlying attachment is a Microsoft Office document
         * (or compatible format). Used by the XML template to conditionally
         * render the office iframe instead of the generic content area.
         */
        isMsOffice: attr({
            compute() {
                return Boolean(this.attachmentOwner && this.attachmentOwner.isMsOffice);
            },
        }),
    },
});

// ─── Patch AttachmentViewer (model) ──────────────────────────────────────────

registerPatch({
    name: "AttachmentViewer",
    fields: {
        /**
         * Current zoom scale for the Office iframe shell.
         */
        officeScale: attr({
            default: 1,
        }),
    },
    recordMethods: {
        /**
         * Zoom in the Office iframe.
         * @param {Object} [opts]
         * @param {boolean} [opts.scroll=false]
         */
        officeZoomIn({ scroll = false } = {}) {
            const step = scroll ? 0.08 : 0.15;
            this.update({ officeScale: Math.min(2.25, (this.officeScale || 1) + step) });
        },

        /**
         * Zoom out the Office iframe.
         * @param {Object} [opts]
         * @param {boolean} [opts.scroll=false]
         */
        officeZoomOut({ scroll = false } = {}) {
            const step = scroll ? 0.08 : 0.15;
            this.update({ officeScale: Math.max(0.45, (this.officeScale || 1) - step) });
        },

        /**
         * Reset the Office iframe zoom to 1.
         */
        officeResetZoom() {
            this.update({ officeScale: 1 });
        },

        /**
         * Open the current Office document in a new browser tab.
         */
        openOfficeInNewTab() {
            if (this.attachmentViewerViewable) {
                browser.open(this.attachmentViewerViewable.defaultSource, "_blank");
            }
        },
    },
});

// ─── Patch AttachmentViewer component ────────────────────────────────────────

import { registerMessagingComponent } from "@mail/utils/messaging_component";
// We patch the prototype after Odoo has registered the component.
// We listen for DOMContentLoaded to ensure the class already exists, or we
// use the owl hooks approach in the patched setup.

// Grab the AttachmentViewer class reference from the OWL registry.
// In Odoo 16, messaging components are keyed by their template name.
const { Component, onMounted } = owl;
import { AttachmentViewer } from "@mail/components/attachment_viewer/attachment_viewer";

// monkey-patch the AttachmentViewer class
const _originalSetup = AttachmentViewer.prototype.setup;
AttachmentViewer.prototype.setup = function () {
    _originalSetup.call(this);
    // nothing extra needed – model fields handle zoom state
};

/**
 * Returns the CSS transform style for the office shell div.
 */
AttachmentViewer.prototype.map2OfficeShellStyle = function () {
    if (!this.attachmentViewer || !this.attachmentViewer.exists()) return "";
    const s = this.attachmentViewer.officeScale || 1;
    return `transform: scale(${s}); transform-origin: center center;`;
};

/**
 * Called when the mouse wheel rolls over the office iframe wrapper.
 */
AttachmentViewer.prototype.map2OnWheelOffice = function (ev) {
    if (!this.attachmentViewer || !this.attachmentViewer.exists()) return;
    if (ev.deltaY > 0) {
        this.attachmentViewer.officeZoomOut({ scroll: true });
    } else {
        this.attachmentViewer.officeZoomIn({ scroll: true });
    }
};

// Extend keydown to handle + / - / 0 when viewing an office document.
const _originalKeydown = AttachmentViewer.prototype._onKeydown;
AttachmentViewer.prototype._onKeydown = function (ev) {
    if (_originalKeydown) _originalKeydown.call(this, ev);
    if (
        !this.attachmentViewer ||
        !this.attachmentViewer.exists() ||
        !this.attachmentViewer.attachmentViewerViewable ||
        !this.attachmentViewer.attachmentViewerViewable.isMsOffice
    ) {
        return;
    }
    switch (ev.key) {
        case "+":
        case "=":
            this.attachmentViewer.officeZoomIn();
            break;
        case "-":
        case "_":
            this.attachmentViewer.officeZoomOut();
            break;
        case "0":
            this.attachmentViewer.officeResetZoom();
            break;
        default:
            return;
    }
    ev.stopPropagation();
};
