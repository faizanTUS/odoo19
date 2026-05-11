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
    "application/vnd.ms-excel.sheet.macroenabled.12",
    "application/vnd.ms-word.document.macroenabled.12",
    "application/vnd.ms-powerpoint.presentation.macroenabled.12",
    "application/rtf",
    "text/rtf",
]);

const OFFICE_EXTENSIONS = new Set([
    "doc", "docx", "xls", "xlsx", "ppt", "pptx", "odt", "ods", "odp", "rtf",
]);

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

// In Odoo 18, mail models use a different structure. 
// Let's try to add the field in a safer way.
try {
    if (Attachment.fields) {
        if (!Attachment.fields.includes('access_token')) {
            Attachment.fields.push('access_token');
        }
    }
} catch (e) {
    console.warn("Could not patch Attachment fields", e);
}

patch(Attachment.prototype, {
    get isMsOffice() {
        if (this.mimetype && OFFICE_MIMETYPES.has(this.mimetype)) return true;
        const ext = (this.extension || (this.filename && this.filename.includes(".") && this.filename.split(".").pop()) || "").toLowerCase();
        return OFFICE_EXTENSIONS.has(ext);
    },

    get isText() {
        if (super.isText) return true;
        return (this.mimetype === 'text/csv' || this.extension === 'csv');
    },

    get isVideo() {
        return super.isVideo || EXTRA_VIDEO_TYPES.includes(this.mimetype);
    },

    get isViewable() {
        if (this.voice) return false;
        if (super.isViewable || this.isText) return true;
        return !this.uploading && this.isMsOffice && officePreviewEnabled();
    },

    get defaultSource() {
        if (this.isText && (this.extension === 'csv' || this.mimetype === 'text/csv')) {
            const queryParams = { id: this.id, download: 'false', mimetype: 'text/plain' };
            if (this.accessToken) queryParams.access_token = this.accessToken;
            return url('/web/content', queryParams);
        }
        
        if (this.isMsOffice && officePreviewEnabled()) {
            const queryParams = { id: this.id, download: 'false' };
            if (this.accessToken) queryParams.access_token = this.accessToken;
            
            const route = url('/web/content', queryParams);
            const absoluteUrl = route.startsWith("/") ? `${browser.location.origin}${route}` : route;

            // console.log("MAP2 DEBUG - Chatter URL:", absoluteUrl, "Token:", this.accessToken);

            if (useGoogleViewer()) {
                return `https://docs.google.com/gview?embedded=true&url=${encodeURIComponent(absoluteUrl)}`;
            }
            return `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(absoluteUrl)}`;
        }
        return super.defaultSource;
    },
});
