/** @odoo-module **/

import { FileModelMixin } from "@web/core/file_viewer/file_model";
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

const CORE_VIDEO_MIMES = [
    "audio/mpeg",
    "video/x-matroska",
    "video/mp4",
    "video/webm",
];

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

function officePreviewEnabled() {
    return session.map2_office_preview !== false;
}

function useGoogleViewer() {
    return Boolean(session.map2_google_viewer_fallback);
}

const PreviewFileBase = FileModelMixin(class {});

/**
 * Lightweight file model for ir.attachment rows shown in many2many_binary (not mail.store).
 */
export class PreviewableIrAttachment extends PreviewFileBase {
    constructor(vals) {
        super();
        Object.assign(this, {
            type: "binary",
            uploading: false,
            ...vals,
        });
        if (!this.filename) {
            this.filename = this.name;
        }
        if (!this.extension && this.name && this.name.includes(".")) {
            this.extension = this.name.split(".").pop().toLowerCase();
        }
    }

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
    }

    get isVideo() {
        if (this.mimetype && CORE_VIDEO_MIMES.includes(this.mimetype)) {
            return true;
        }
        return EXTRA_VIDEO_TYPES.includes(this.mimetype);
    }

    get isViewable() {
        if (this.voice) {
            return false;
        }
        const baseViewable =
            (this.isText || this.isImage || this.isVideo || this.isPdf || this.isUrlYoutube) &&
            !this.uploading;
        if (baseViewable) {
            return true;
        }
        if (!this.uploading && this.isMsOffice && officePreviewEnabled()) {
            return true;
        }
        return false;
    }

    get defaultSource() {
        if (this.isMsOffice && officePreviewEnabled()) {
            const route = url(this.urlRoute, this.urlQueryParams);
            const absoluteUrl = `${browser.location.origin}${route}`;
            if (useGoogleViewer()) {
                return `https://docs.google.com/gview?embedded=true&url=${encodeURIComponent(absoluteUrl)}`;
            }
            return `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(absoluteUrl)}`;
        }
        return super.defaultSource;
    }
}
