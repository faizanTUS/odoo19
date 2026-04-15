/** @odoo-module **/

import { registerPatch } from "@mail/model/model_core";
import { attr } from "@mail/model/model_field";
import { browser } from "@web/core/browser/browser";
import { session } from "@web/session";

const OFFICE_MIMETYPES = new Set([
    "application/msword",
    "application/vnd.ms-word",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.oasis.opendocument.text",
    "application/vnd.oasis.opendocument.spreadsheet",
    "application/vnd.oasis.opendocument.presentation",
    "text/csv",
    "application/csv",
    "application/vnd.ms-excel.sheet.macroenabled.12",
    "application/vnd.ms-word.document.macroenabled.12",
    "application/vnd.ms-powerpoint.presentation.macroenabled.12",
    "application/rtf",
    "text/rtf",
]);

const OFFICE_EXTENSIONS = new Set([
    "doc",
    "docx",
    "xls",
    "xlsx",
    "ppt",
    "pptx",
    "odt",
    "ods",
    "odp",
    "csv",
    "rtf",
]);

const EXTRA_VIDEO_TYPES = [
    "video/ogg",
    "video/quicktime",
    "video/x-msvideo",
    "video/3gpp",
    "video/mpeg",
    "audio/ogg",
    "audio/wav",
    "audio/x-wav",
    "audio/mp4",
    "audio/webm",
];

function uapOfficePreviewEnabled() {
    return session.uap_office_preview !== false;
}

function uapUseGoogleViewer() {
    return Boolean(session.uap_google_office_fallback);
}

function absoluteAttachmentUrl(attachment) {
    const origin = browser.location.origin;
    if (
        !attachment.accessToken &&
        attachment.originThread &&
        attachment.originThread.model === "mail.channel"
    ) {
        return `${origin}/mail/channel/${attachment.originThread.id}/attachment/${attachment.id}`;
    }
    const token = attachment.accessToken
        ? `?access_token=${encodeURIComponent(attachment.accessToken)}`
        : "";
    return `${origin}/web/content/${attachment.id}${token}`;
}

registerPatch({
    name: "Attachment",
    fields: {
        isMsOffice: attr({
            compute() {
                if (this.mimetype && OFFICE_MIMETYPES.has(this.mimetype)) {
                    return true;
                }
                const ext = (
                    this.extension ||
                    (this.filename &&
                        this.filename.includes(".") &&
                        this.filename.split(".").pop()) ||
                    ""
                ).toLowerCase();
                return OFFICE_EXTENSIONS.has(ext);
            },
        }),
        defaultSource: {
            compute() {
                if (this.isMsOffice && uapOfficePreviewEnabled()) {
                    const absoluteUrl = absoluteAttachmentUrl(this);
                    if (uapUseGoogleViewer()) {
                        return `https://docs.google.com/gview?embedded=true&url=${encodeURIComponent(
                            absoluteUrl
                        )}`;
                    }
                    return `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(
                        absoluteUrl
                    )}`;
                }
                return this._super();
            },
        },
        isVideo: {
            compute() {
                if (this._super()) {
                    return true;
                }
                return EXTRA_VIDEO_TYPES.includes(this.mimetype);
            },
        },
        isViewable: {
            compute() {
                if (this._super()) {
                    return true;
                }
                if (!this.isUploading && this.isMsOffice && uapOfficePreviewEnabled()) {
                    return true;
                }
                return false;
            },
        },
    },
});

registerPatch({
    name: "AttachmentViewerViewable",
    fields: {
        isMsOffice: attr({
            compute() {
                return this.attachmentOwner.isMsOffice;
            },
        }),
    },
});

registerPatch({
    name: "AttachmentViewer",
    fields: {
        officeScale: attr({
            default: 1,
        }),
    },
    recordMethods: {
        next() {
            this._super();
            if (this.exists()) {
                this.update({ officeScale: 1 });
            }
        },
        previous() {
            this._super();
            if (this.exists()) {
                this.update({ officeScale: 1 });
            }
        },
        officeZoomIn(arg) {
            let scroll = false;
            if (arg && typeof arg === "object" && "scroll" in arg) {
                scroll = arg.scroll;
            } else if (arg && typeof arg.stopPropagation === "function") {
                arg.stopPropagation();
            }
            const step = scroll ? 0.08 : 0.15;
            const next = Math.min(2.25, (this.officeScale || 1) + step);
            this.update({ officeScale: next });
        },
        officeZoomOut(arg) {
            let scroll = false;
            if (arg && typeof arg === "object" && "scroll" in arg) {
                scroll = arg.scroll;
            } else if (arg && typeof arg.stopPropagation === "function") {
                arg.stopPropagation();
            }
            const step = scroll ? 0.08 : 0.15;
            const next = Math.max(0.45, (this.officeScale || 1) - step);
            this.update({ officeScale: next });
        },
        officeResetZoom(arg) {
            if (arg && typeof arg.stopPropagation === "function") {
                arg.stopPropagation();
            }
            this.update({ officeScale: 1 });
        },
        onWheelOffice(ev) {
            ev.stopPropagation();
            if (ev.deltaY > 0) {
                this.officeZoomOut({ scroll: true });
            } else {
                this.officeZoomIn({ scroll: true });
            }
        },
        openOfficeInNewTab(ev) {
            if (ev) {
                ev.stopPropagation();
            }
            const url = this.attachmentViewerViewable.defaultSource;
            browser.open(url, "_blank");
        },
    },
});
