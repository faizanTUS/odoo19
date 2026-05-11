/** @odoo-module **/

/**
 * Odoo 16 - Patch the mail Attachment model to support:
 *   - isMsOffice detection
 *   - Extended isVideo (extra MIME types)
 *   - Extended isText (CSV)
 *   - Extended isViewable (Office docs when preview enabled)
 *   - defaultSource override for Office online / Google Docs viewer
 */

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

function buildContentUrl(id, accessToken, extraParams = {}) {
    const params = new URLSearchParams({ id: String(id), download: "false", ...extraParams });
    if (accessToken) params.set("access_token", accessToken);
    return `/web/content?${params.toString()}`;
}

function toAbsolute(route) {
    return route.startsWith("/") ? `${browser.location.origin}${route}` : route;
}

registerPatch({
    name: "Attachment",
    modelMethods: {
        /**
         * @override
         */
        convertData(data) {
            const data2 = this._super(data);
            if ('file_size' in data) {
                data2.file_size = data.file_size;
            }
            return data2;
        },
    },
    fields: {
        /**
         * Size of the file in bytes. (New field)
         */
        file_size: attr(),
        /**
         * Human readable size (e.g. 1.2 MB). (New field)
         */
        file_size_human: attr({
            compute() {
                if (!this.file_size) return "";
                const units = ["B", "KB", "MB", "GB", "TB"];
                let size = this.file_size;
                let i = 0;
                while (size >= 1000 && i < units.length - 1) {
                    size /= 1000;
                    i++;
                }
                return `${size.toFixed(2)} ${units[i]}`;
            },
        }),
        /**
         * Whether this attachment is a Microsoft Office (or compatible) document. (New field)
         */
        isMsOffice: attr({
            compute() {
                if (this.mimetype && OFFICE_MIMETYPES.has(this.mimetype)) return true;
                const name = this.filename || this.name || "";
                const ext = name.includes(".") ? name.split(".").pop().toLowerCase() : "";
                return OFFICE_EXTENSIONS.has(ext);
            },
        }),
        /**
         * Existing field override: also treat CSV as text.
         * NOTE: When patching EXISTING fields in recordMethods/fields, 
         * DO NOT use attr() as it introduces 'fieldType' which Odoo 16 patcher rejects.
         */
        isText: {
            compute() {
                const textMimeType = [
                    "application/javascript",
                    "application/json",
                    "text/css",
                    "text/html",
                    "text/plain",
                    "text/csv",
                ];
                if (textMimeType.includes(this.mimetype)) return true;
                const name = this.filename || this.name || "";
                const ext = name.includes(".") ? name.split(".").pop().toLowerCase() : "";
                return ext === "csv";
            },
        },
        /**
         * Existing field override: extend with extra video/audio MIME types.
         */
        isVideo: {
            compute() {
                const videoMimeTypes = [
                    "audio/mpeg",
                    "video/x-matroska",
                    "video/mp4",
                    "video/webm",
                    ...EXTRA_VIDEO_TYPES,
                ];
                return videoMimeTypes.includes(this.mimetype);
            },
        },
        /**
         * Existing field override: also viewable when isOffice + office preview enabled.
         */
        isViewable: {
            compute() {
                if (this.isText || this.isImage || this.isVideo || this.isPdf || this.isUrlYoutube) {
                    return true;
                }
                return this.isMsOffice && officePreviewEnabled();
            },
        },
        /**
         * Existing field override: inject Office viewer URL when applicable.
         */
        defaultSource: {
            compute() {
                // CSV/text: force text/plain MIME so iframe shows raw text
                if (this.isText && (this.mimetype === "text/csv" || (this.filename || "").endsWith(".csv"))) {
                    return buildContentUrl(this.id, this.accessToken, { mimetype: "text/plain" });
                }

                // Office documents → embed in external viewer
                if (this.isMsOffice && officePreviewEnabled()) {
                    const route = buildContentUrl(this.id, this.accessToken);
                    const absoluteUrl = toAbsolute(route);
                    if (useGoogleViewer()) {
                        return `https://docs.google.com/gview?embedded=true&url=${encodeURIComponent(absoluteUrl)}`;
                    }
                    return `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(absoluteUrl)}`;
                }

                // Fallback: Odoo 16 core logic (image, pdf, youtube, video, text)
                if (this.isImage) {
                    return `/web/image/${this.id}?signature=${this.checksum}`;
                }
                if (this.isPdf) {
                    const pdfLib = `/web/static/lib/pdfjs/web/viewer.html?file=`;
                    if (!this.accessToken && this.originThread && this.originThread.model === "mail.channel") {
                        return `${pdfLib}/mail/channel/${this.originThread.id}/attachment/${this.id}#pagemode=none`;
                    }
                    const token = this.accessToken ? `?access_token%3D${this.accessToken}` : "";
                    return `${pdfLib}/web/content/${this.id}${token}#pagemode=none`;
                }
                if (this.isUrlYoutube) {
                    const urlArr = this.url.split("/");
                    let token = urlArr[urlArr.length - 1];
                    if (token.includes("watch")) {
                        token = token.split("v=")[1];
                        const amp = token.indexOf("&");
                        if (amp !== -1) token = token.substring(0, amp);
                    }
                    return `https://www.youtube.com/embed/${token}`;
                }
                if (!this.accessToken && this.originThread && this.originThread.model === "mail.channel") {
                    return `/mail/channel/${this.originThread.id}/attachment/${this.id}`;
                }
                const accessToken = this.accessToken ? `?access_token=${this.accessToken}` : "";
                return `/web/content/${this.id}${accessToken}`;
            },
        },
    },
});
