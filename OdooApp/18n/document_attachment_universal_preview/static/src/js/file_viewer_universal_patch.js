/** @odoo-module **/

import { FileViewer } from "@web/core/file_viewer/file_viewer";
import { patch } from "@web/core/utils/patch";
import { browser } from "@web/core/browser/browser";

patch(FileViewer.prototype, {
    setup() {
        super.setup();
        this.officeScrollZoomStep = 0.08;
        this.officeZoomStep = 0.15;
        this.minOfficeScale = 0.45;
        this.maxOfficeScale = 2.25;
        this.state.officeScale = 1;
    },

    activateFile(index) {
        super.activateFile(index);
        this.state.officeScale = 1;
    },

    get officeShellStyle() {
        const s = this.state.officeScale ?? 1;
        return `transform: scale(${s}); transform-origin: center center;`;
    },

    officeZoomIn({ scroll = false } = {}) {
        const step = scroll ? this.officeScrollZoomStep : this.officeZoomStep;
        this.state.officeScale = Math.min(this.maxOfficeScale, (this.state.officeScale ?? 1) + step);
    },

    officeZoomOut({ scroll = false } = {}) {
        const step = scroll ? this.officeScrollZoomStep : this.officeZoomStep;
        this.state.officeScale = Math.max(
            this.minOfficeScale,
            (this.state.officeScale ?? 1) - step
        );
    },

    officeResetZoom() {
        this.state.officeScale = 1;
    },

    onWheelOffice(ev) {
        if (ev.deltaY > 0) {
            this.officeZoomOut({ scroll: true });
        } else {
            this.officeZoomIn({ scroll: true });
        }
    },

    openOfficeInNewTab() {
        browser.open(this.state.file.defaultSource, "_blank");
    },

    onKeydown(ev) {
        super.onKeydown(ev);
        if (!this.state.file.isMsOffice) {
            return;
        }
        switch (ev.key) {
            case "+":
            case "=":
                this.officeZoomIn();
                break;
            case "-":
            case "_":
                this.officeZoomOut();
                break;
            case "0":
                this.officeResetZoom();
                break;
        }
    },
});
