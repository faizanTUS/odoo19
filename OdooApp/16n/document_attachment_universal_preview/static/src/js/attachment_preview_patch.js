/** @odoo-module **/

import { registerPatch } from "@mail/model/model_core";
import { attr } from "@mail/model/model_field";
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

function extractExt(attachment) {
    const raw = attachment.extension || attachment.filename || attachment.name || "";
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
    const publicBaseUrl = ((window.location && window.location.origin) || session.uap_base_url || "").replace(/\/$/, "");
    if (!publicBaseUrl) {
        return route;
    }
    return new URL(route, `${publicBaseUrl}/`).toString();
}

registerPatch({
    name: "Attachment",
    fields: {
        isMsOffice: attr({
            compute() {
                const ext = extractExt(this);
                if (LOCAL_TEXT_PREVIEW_EXTENSIONS.has(ext)) {
                    return false;
                }
                if (this.mimetype && OFFICE_MIMETYPES.has(this.mimetype)) {
                    return true;
                }
                return OFFICE_EXTENSIONS.has(ext);
            },
        }),
        isVideo: {
            compute() {
                const videoMimeTypes = [
                    "audio/mpeg",
                    "video/x-matroska",
                    "video/mp4",
                    "video/webm",
                ];
                return videoMimeTypes.includes(this.mimetype) || EXTRA_VIDEO_TYPES.includes(this.mimetype);
            },
        },
        isText: {
            compute() {
                const ext = extractExt(this);
                const textMimeType = [
                    "application/javascript",
                    "application/json",
                    "text/css",
                    "text/html",
                    "text/plain",
                ];
                return textMimeType.includes(this.mimetype) || LOCAL_TEXT_PREVIEW_EXTENSIONS.has(ext) || CSV_MIMETYPES.has(this.mimetype) || RTF_MIMETYPES.has(this.mimetype);
            },
        },
        isPdf: {
            compute() {
                return this.mimetype === "application/pdf" || (this.isMsOffice && uapOfficePreviewEnabled());
            },
        },
        isViewable: {
            compute() {
                return this.isText || this.isImage || this.isVideo || this.isPdf || this.isUrlYoutube;
            },
        },
        defaultSource: {
            compute() {
                const ext = extractExt(this);
                if (LOCAL_TEXT_PREVIEW_EXTENSIONS.has(ext)) {
                    return `/uap/preview/${this.id}/${this.checksum || "none"}?filename=${encodeURIComponent(
                        this.name || this.filename || "document"
                    )}&inline=1&as_text=1`;
                }
                if (this.isMsOffice && uapOfficePreviewEnabled()) {
                    const route = `/uap/preview/${this.id}/${this.checksum || "none"}?filename=${encodeURIComponent(
                        this.name || this.filename || "document"
                    )}&inline=1`;
                    const absoluteUrl = toAbsolutePreviewUrl(route);
                    if (uapUseGoogleViewer()) {
                        return `https://docs.google.com/gview?embedded=true&url=${encodeURIComponent(absoluteUrl)}`;
                    }
                    return `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(absoluteUrl)}`;
                }
                if (this.isImage) {
                    return `/web/image/${this.id}?signature=${this.checksum}`;
                }
                if (this.isPdf) {
                    const pdfLib = "/web/static/lib/pdfjs/web/viewer.html?file=";
                    if (!this.accessToken && this.originThread && this.originThread.model === "mail.channel") {
                        return `${pdfLib}/mail/channel/${this.originThread.id}/attachment/${this.id}#pagemode=none`;
                    }
                    const accessToken = this.accessToken ? `?access_token%3D${this.accessToken}` : "";
                    return `${pdfLib}/web/content/${this.id}${accessToken}#pagemode=none`;
                }
                if (this.isUrlYoutube) {
                    const urlArr = this.url.split("/");
                    let token = urlArr[urlArr.length - 1];
                    if (token.includes("watch")) {
                        token = token.split("v=")[1];
                        const amp = token.indexOf("&");
                        if (amp !== -1) {
                            token = token.substring(0, amp);
                        }
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

registerPatch({
    name: "AttachmentViewerViewable",
    fields: {
        isMsOffice: attr({
            compute() {
                return Boolean(this.attachmentOwner && this.attachmentOwner.isMsOffice);
            },
        }),
    },
});
