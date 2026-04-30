/** @odoo-module **/

/**
 * Odoo 16 - Patch Many2ManyBinaryField to:
 *   1. Fetch extra fields (access_token, file_size) for each attachment record.
 *   2. Add an eye-icon preview button next to each file.
 *   3. Open a full-screen preview dialog when clicked.
 *
 * The preview dialog is a lightweight OWL component that embeds the file
 * in an <iframe> (for PDF / Office / text) or <img>/<video> tag.
 */

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { browser } from "@web/core/browser/browser";
import { session } from "@web/session";
import {
    Many2ManyBinaryField,
} from "@web/views/fields/many2many_binary/many2many_binary_field";

import { Component, xml } from "@odoo/owl";

// ─── Constants ───────────────────────────────────────────────────────────────

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

const IMAGE_MIMETYPES = new Set([
    "image/bmp", "image/gif", "image/jpeg", "image/png",
    "image/svg+xml", "image/tiff", "image/x-icon", "image/webp",
]);

const VIDEO_MIMETYPES = new Set([
    "audio/mpeg", "video/x-matroska", "video/mp4", "video/webm",
    "video/ogg", "video/quicktime", "video/x-msvideo", "video/3gpp", "video/mpeg",
    "audio/ogg", "audio/wav", "audio/x-wav", "audio/mp4", "audio/webm",
]);

const TEXT_MIMETYPES = new Set([
    "text/plain", "text/html", "text/css", "application/json",
    "application/javascript", "text/csv",
]);

// ─── Helpers ─────────────────────────────────────────────────────────────────

function officePreviewEnabled() {
    return session.map2_office_preview !== false;
}

function useGoogleViewer() {
    return Boolean(session.map2_google_viewer_fallback);
}

function getFileExt(file) {
    const name = file.name || "";
    return name.includes(".") ? name.split(".").pop().toLowerCase() : "";
}

function isOfficeFile(file) {
    if (file.mimetype && OFFICE_MIMETYPES.has(file.mimetype)) return true;
    return OFFICE_EXTENSIONS.has(getFileExt(file));
}

function isImageFile(file) {
    return file.mimetype && IMAGE_MIMETYPES.has(file.mimetype);
}

function isVideoFile(file) {
    return file.mimetype && VIDEO_MIMETYPES.has(file.mimetype);
}

function isPdfFile(file) {
    return file.mimetype === "application/pdf";
}

function isTextFile(file) {
    if (file.mimetype && TEXT_MIMETYPES.has(file.mimetype)) return true;
    return getFileExt(file) === "csv";
}

function isPreviewable(file) {
    if (isImageFile(file) || isVideoFile(file) || isPdfFile(file) || isTextFile(file)) {
        return true;
    }
    return isOfficeFile(file) && officePreviewEnabled();
}

function buildPreviewUrl(file) {
    const token = file.access_token || file.accessToken || file.token;
    const base = `/web/content?id=${file.id}&download=false`;
    const withToken = token ? `${base}&access_token=${token}` : base;

    if (isTextFile(file)) {
        return `${withToken}&mimetype=${encodeURIComponent("text/plain")}`;
    }
    if (isOfficeFile(file) && officePreviewEnabled()) {
        const absoluteUrl = toAbsolute(withToken);
        if (useGoogleViewer()) {
            return `https://docs.google.com/gview?embedded=true&url=${encodeURIComponent(absoluteUrl)}`;
        }
        return `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(absoluteUrl)}`;
    }
    if (isPdfFile(file)) {
        const pdfLib = `/web/static/lib/pdfjs/web/viewer.html?file=`;
        const filePath = token ? `/web/content/${file.id}?access_token%3D${token}` : `/web/content/${file.id}`;
        return `${pdfLib}${filePath}#pagemode=none`;
    }
    if (isImageFile(file)) {
        return `/web/image/${file.id}?signature=${file.checksum || ""}`;
    }
    if (isVideoFile(file)) {
        return token ? `/web/content/${file.id}?access_token=${token}` : `/web/content/${file.id}`;
    }
    return withToken;
}

function toAbsolute(route) {
    return route.startsWith("/") ? `${browser.location.origin}${route}` : route;
}

// ─── Preview Dialog Component ─────────────────────────────────────────────────

/**
 * A fullscreen preview dialog showing an <iframe>, <img>, or <video> based on
 * the file's MIME type. Supports navigating across the previewable list.
 */
class Map2AttachmentPreviewDialog extends Component {
    setup() {
        this.state = owl.useState({
            currentIndex: this.props.initialIndex || 0,
            scale: 1,
        });
    }

    get files() {
        return this.props.files || [];
    }

    get currentFile() {
        return this.files[this.state.currentIndex] || null;
    }

    get previewSrc() {
        return this.currentFile ? buildPreviewUrl(this.currentFile) : "";
    }

    get isImage() {
        return this.currentFile && isImageFile(this.currentFile);
    }

    get isVideo() {
        return this.currentFile && isVideoFile(this.currentFile);
    }

    get isIframe() {
        // Everything else: PDF, Office, Text → iframe
        const f = this.currentFile;
        return f && !isImageFile(f) && !isVideoFile(f);
    }

    get hasPrev() {
        return this.state.currentIndex > 0;
    }

    get hasNext() {
        return this.state.currentIndex < this.files.length - 1;
    }

    prev() {
        if (this.hasPrev) {
            this.state.currentIndex--;
            this.state.scale = 1;
        }
    }

    next() {
        if (this.hasNext) {
            this.state.currentIndex++;
            this.state.scale = 1;
        }
    }

    zoomIn() {
        this.state.scale += 0.1;
    }

    zoomOut() {
        if (this.state.scale > 0.2) this.state.scale -= 0.1;
    }

    zoomReset() {
        this.state.scale = 1;
    }

    openInNewTab() {
        if (this.currentFile) {
            browser.open(this.previewSrc, "_blank");
        }
    }
}

Map2AttachmentPreviewDialog.template = xml`
<Dialog header="false" footer="false" size="'fullscreen'" contentClass="'o-map2-preview-dialog d-flex flex-column h-100 p-0 shadow-none'" bodyClass="'d-flex flex-column flex-grow-1 p-0 overflow-hidden bg-dark'">
    <!-- Header -->
    <div class="o_map2_preview_header d-flex align-items-center justify-content-between px-3 py-2 text-white bg-dark">
        <div class="o_map2_preview_filename text-truncate d-flex align-items-center gap-2">
            <span t-if="currentFile" t-esc="currentFile.name"/>
            <span t-if="files.length > 1" class="badge rounded-pill bg-secondary small">
                <t t-esc="state.currentIndex + 1"/> / <t t-esc="files.length"/>
            </span>
        </div>
        <div class="o_map2_preview_actions d-flex align-items-center gap-2">
            <a t-if="currentFile" class="btn btn-link py-0 text-white" t-att-href="'/web/content?id=' + currentFile.id + '&amp;download=true'" title="Download">
                <i class="fa fa-download"/> Download
            </a>
            <button class="btn btn-link py-0 text-white" t-on-click="() => props.close()" title="Close">
                <i class="fa fa-times fa-lg"/>
            </button>
        </div>
    </div>

    <!-- Main Content Area -->
    <div class="flex-grow-1 d-flex align-items-center justify-content-center position-relative overflow-hidden bg-black" style="min-height:0">
        <!-- Navigation Arrows -->
        <t t-if="hasPrev">
            <button class="btn btn-link position-absolute start-0 h-100 px-4 text-white o_map2_nav_btn" t-on-click="prev" style="z-index: 10; opacity: 0.5;">
                <i class="fa fa-chevron-left fa-2x"/>
            </button>
        </t>
        <t t-if="hasNext">
            <button class="btn btn-link position-absolute end-0 h-100 px-4 text-white o_map2_nav_btn" t-on-click="next" style="z-index: 10; opacity: 0.5;">
                <i class="fa fa-chevron-right fa-2x"/>
            </button>
        </t>

        <!-- File Render -->
        <div class="o_map2_preview_wrap d-flex align-items-center justify-content-center w-100 h-100 p-4">
            <t t-if="isImage">
                <img class="img-fluid shadow-lg" t-att-src="previewSrc" t-att-alt="currentFile.name" t-attf-style="max-height: 90vh; transform: scale({{state.scale}}); transition: transform 0.1s;"/>
            </t>
            <t t-elif="isVideo">
                <video class="w-100 h-100" style="max-width: 80vw; max-height: 80vh;" controls="controls">
                    <source t-att-src="previewSrc" t-att-type="currentFile.mimetype"/>
                </video>
            </t>
            <t t-elif="isIframe">
                <div class="w-100 h-100 overflow-hidden d-flex align-items-center justify-content-center bg-white shadow-lg rounded">
                    <iframe class="w-100 h-100 border-0" t-att-src="previewSrc" title="File preview" t-attf-style="transform: scale({{state.scale}}); transform-origin: center center; transition: transform 0.1s;"/>
                </div>
            </t>
        </div>

        <!-- Bottom Controls -->
        <div class="o_map2_preview_footer position-absolute bottom-0 start-50 translate-middle-x mb-4 d-flex align-items-center gap-1 bg-dark px-3 py-1 rounded-pill shadow-lg border border-secondary" style="z-index: 20; opacity: 0.9;">
            <button class="btn btn-link py-0 text-white" t-on-click="zoomIn" title="Zoom In">
                <i class="fa fa-plus"/>
            </button>
            <button class="btn btn-link py-0 text-white" t-on-click="zoomReset" title="Reset Zoom">
                <i class="fa fa-search"/>
            </button>
            <button class="btn btn-link py-0 text-white" t-on-click="zoomOut" title="Zoom Out">
                <i class="fa fa-minus"/>
            </button>
            <div class="vr bg-secondary mx-1" style="width: 1px; height: 1.5rem;"/>
            <button class="btn btn-link py-0 text-white" t-on-click="openInNewTab" title="Open in New Tab">
                <i class="fa fa-external-link"/>
            </button>
        </div>
    </div>
</Dialog>
`;
Map2AttachmentPreviewDialog.components = { Dialog };

// ─── Fetch extra fields on Many2ManyBinaryField ───────────────────────────────

// Odoo 16 uses `fieldsToFetch` (a static object, not an array) to declare
// which fields to load for the related model. We add access_token & file_size.
if (Many2ManyBinaryField.fieldsToFetch) {
    Object.assign(Many2ManyBinaryField.fieldsToFetch, {
        access_token: { type: "char" },
        file_size: { type: "integer" },
    });
}

// ─── Patch Many2ManyBinaryField ───────────────────────────────────────────────

patch(Many2ManyBinaryField.prototype, "tus_many2many_attachment_preview", {
    setup() {
        this._super(...arguments);
        this.dialog = useService("dialog");
    },

    /**
     * Formats file size to human readable string.
     * @param {number} bytes
     */
    map2FormatSize(bytes) {
        if (!bytes) return "";
        const units = ["B", "KB", "MB", "GB", "TB"];
        let size = bytes;
        let i = 0;
        while (size >= 1000 && i < units.length - 1) {
            size /= 1000;
            i++;
        }
        return `${size.toFixed(2)} ${units[i]}`;
    },

    /**
     * Returns only the previewable files (for navigation).
     */
    map2PreviewableList() {
        return (this.files || []).filter(isPreviewable);
    },

    /**
     * Check if a single file is previewable.
     */
    map2IsPreviewable(file) {
        return isPreviewable(file);
    },

    /**
     * Called when the eye-icon button is clicked.
     */
    onPreviewMany2many(file) {
        const previewableFiles = this.map2PreviewableList();
        if (!previewableFiles.length || !isPreviewable(file)) {
            this.notification.add(
                _t("There is no in-browser preview for this file type. Use Download instead."),
                { type: "info" }
            );
            return;
        }
        const initialIndex = previewableFiles.findIndex((f) => f.id === file.id);
        this.dialog.add(Map2AttachmentPreviewDialog, {
            files: previewableFiles,
            initialIndex: initialIndex >= 0 ? initialIndex : 0,
        });
    },
});
