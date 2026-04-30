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
    "application/vnd.ms-excel.sheet.macroenabled.12",
    "application/vnd.ms-word.document.macroenabled.12",
    "application/vnd.ms-powerpoint.presentation.macroenabled.12",
    "application/rtf",
    "text/rtf",
]);

const OFFICE_EXTENSIONS = new Set([
    "doc", "docx", "xls", "xlsx", "ppt", "pptx", "odt", "ods", "odp", "rtf",
]);

const CORE_VIDEO_MIMES = ["audio/mpeg", "video/x-matroska", "video/mp4", "video/webm"];
const EXTRA_VIDEO_TYPES = [
    "video/ogg", "video/quicktime", "video/x-msvideo", "video/3gpp", "video/mpeg",
    "audio/ogg", "audio/wav", "audio/x-wav", "audio/mp4", "audio/webm",
];

function officePreviewEnabled() {
    return session.map2_office_preview !== false;
}

function useGoogleViewer() {
    return Boolean(session.map2_google_viewer_fallback);
}

const PreviewFileBase = FileModelMixin(class {});

export class PreviewableIrAttachment extends PreviewFileBase {
    constructor(vals) {
        super();
        Object.assign(this, {
            type: "binary",
            uploading: false,
            ...vals,
        });
        if (!this.filename) this.filename = this.name;
        if (!this.extension && this.name && this.name.includes(".")) {
            this.extension = this.name.split(".").pop().toLowerCase();
        }
    }

    get isText() {
        // Force CSV and RTF to be viewable as text if Office fails
        if (super.isText) return true;
        return (this.mimetype === 'text/csv' || this.extension === 'csv');
    }

    get isMsOffice() {
        if (this.mimetype && OFFICE_MIMETYPES.has(this.mimetype)) return true;
        const ext = (this.extension || (this.filename && this.filename.includes(".") && this.filename.split(".").pop()) || "").toLowerCase();
        return OFFICE_EXTENSIONS.has(ext);
    }

    get isVideo() {
        return (this.mimetype && CORE_VIDEO_MIMES.includes(this.mimetype)) || EXTRA_VIDEO_TYPES.includes(this.mimetype);
    }

    get isViewable() {
        if (this.voice) return false;
        const baseViewable = (this.isText || this.isImage || this.isVideo || this.isPdf || this.isUrlYoutube) && !this.uploading;
        if (baseViewable || (this.type === "url" && this.url)) return true;
        return !this.uploading && this.isMsOffice && officePreviewEnabled();
    }

    get defaultSource() {
        if (this.type === "url" && this.url) return this.url;
        
        // Force CSV/RTF to be text stream if they are viewed as text
        if (this.isText && (this.extension === 'csv' || this.mimetype === 'text/csv')) {
            const queryParams = { 
                id: this.id, 
                download: 'false',
                mimetype: 'text/plain' // Force browser to show as text
            };
            if (this.access_token) queryParams.access_token = this.access_token;
            return url('/web/content', queryParams);
        }

        if (this.isMsOffice && officePreviewEnabled()) {
            const queryParams = { id: this.id, download: 'false' };
            if (this.access_token) queryParams.access_token = this.access_token;
            
            const route = url('/web/content', queryParams);
            const absoluteUrl = route.startsWith("/") ? `${browser.location.origin}${route}` : route;
            
            // console.log("MAP2 DEBUG - URL for Office:", absoluteUrl, "Token:", this.access_token);

            if (useGoogleViewer()) {
                return `https://docs.google.com/gview?embedded=true&url=${encodeURIComponent(absoluteUrl)}`;
            }
            return `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(absoluteUrl)}`;
        }
        return super.defaultSource;
    }
}
