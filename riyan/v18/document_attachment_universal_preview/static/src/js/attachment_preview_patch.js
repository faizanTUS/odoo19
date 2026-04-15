/** @odoo-module **/

import { Attachment } from "@mail/core/common/attachment_model";
import { patch } from "@web/core/utils/patch";
import { url } from "@web/core/utils/urls";
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

patch(Attachment.prototype, {
    get isMsOffice() {
        if (this.mimetype && OFFICE_MIMETYPES.has(this.mimetype)) {
            return true;
        }
        const ext = (
            this.extension ||
            (this.filename && this.filename.includes(".") && this.filename.split(".").pop()) ||
            ""
        ).toLowerCase();
        return OFFICE_EXTENSIONS.has(ext);
    },

    get isVideo() {
        if (super.isVideo) {
            return true;
        }
        return EXTRA_VIDEO_TYPES.includes(this.mimetype);
    },

    get isViewable() {
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
        if (this.isMsOffice && uapOfficePreviewEnabled()) {
            const route = url(this.urlRoute, this.urlQueryParams);
            const absoluteUrl = `${browser.location.origin}${route}`;
            if (uapUseGoogleViewer()) {
                return `https://docs.google.com/gview?embedded=true&url=${encodeURIComponent(absoluteUrl)}`;
            }
            return `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(absoluteUrl)}`;
        }
        return super.defaultSource;
    },
});
