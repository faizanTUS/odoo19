/** @odoo-module **/

import { Attachment } from "@mail/core/common/attachment_model";
import { patch } from "@web/core/utils/patch";
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

const CSV_MIMETYPES = new Set(["text/csv", "application/csv"]);
const RTF_MIMETYPES = new Set(["application/rtf", "text/rtf"]);
const LOCAL_TEXT_PREVIEW_EXTENSIONS = new Set(["csv", "rtf"]);

function extractExt(file) {
    const raw = file.extension || file.filename || file.name || "";
    const clean = String(raw).trim().toLowerCase();
    if (clean.includes(".")) {
        return clean.split(".").pop().trim();
    }
    return clean;
}

function uapOfficePreviewEnabled() {
    return session.uap_office_preview !== false;
}

function uapUseGoogleViewer() {
    return Boolean(session.uap_google_office_fallback);
}

function toAbsolutePreviewUrl(route) {
    if (!route) {
        return route;
    }
    if (/^https?:\/\//i.test(route)) {
        return route;
    }
    const publicBaseUrl = (browser.location.origin || session.uap_base_url || "").replace(/\/$/, "");
    if (!publicBaseUrl) {
        return route;
    }
    return new URL(route, `${publicBaseUrl}/`).toString();
}

patch(Attachment.prototype, {
    get isMsOffice() {
        const ext = extractExt(this);
        if (LOCAL_TEXT_PREVIEW_EXTENSIONS.has(ext)) {
            return false;
        }
        if (this.mimetype && OFFICE_MIMETYPES.has(this.mimetype)) {
            return true;
        }
        return OFFICE_EXTENSIONS.has(ext);
    },

    get isVideo() {
        if (super.isVideo) {
            return true;
        }
        return EXTRA_VIDEO_TYPES.includes(this.mimetype);
    },

    get isText() {
        const ext = extractExt(this);
        if (LOCAL_TEXT_PREVIEW_EXTENSIONS.has(ext)) {
            return true;
        }
        if (super.isText) {
            return true;
        }
        return LOCAL_TEXT_PREVIEW_EXTENSIONS.has(ext) || CSV_MIMETYPES.has(this.mimetype) || RTF_MIMETYPES.has(this.mimetype);
    },

    get isViewable() {
        const ext = extractExt(this);
        if (!this.uploading && LOCAL_TEXT_PREVIEW_EXTENSIONS.has(ext)) {
            return true;
        }
        if (this.voice) {
            return false;
        }
        if (super.isViewable) {
            return true;
        }
        if (!this.uploading && this.isMsOffice && uapOfficePreviewEnabled()) {
            return true;
        }
        return false;
    },

    get defaultSource() {
        const ext = extractExt(this);

        // Keep CSV / RTF on module preview route and force inline text rendering.
        if (LOCAL_TEXT_PREVIEW_EXTENSIONS.has(ext)) {
            return `/uap/preview/${this.id}/${this.checksum || "none"}?filename=${encodeURIComponent(
                this.name || this.filename || "document"
            )}&inline=1&as_text=1`;
        }

        if (this.isMsOffice && uapOfficePreviewEnabled()) {
            const route = `/uap/preview/${this.id}/${this.checksum || "none"}?filename=${encodeURIComponent(
                this.name || this.filename || "document"
            )}`;
            const absoluteUrl = toAbsolutePreviewUrl(route);

            if (uapUseGoogleViewer()) {
                return `https://docs.google.com/gview?embedded=true&url=${encodeURIComponent(absoluteUrl)}`;
            }
            return `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(absoluteUrl)}`;
        }
        return super.defaultSource;
    },
});
