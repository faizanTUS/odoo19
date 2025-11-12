/** @odoo-module **/

import { Component, useState, useRef } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { useService } from "@web/core/utils/hooks";


export class ImageSearchDialog extends Component {
    static template = "ai_odoo_website_product_image_search.ImageSearchDialog";
    static components = { Dialog };

    setup() {
        this.state = useState({
            imageFile: null,
            previewData: null,
            dragging: false,
        });
        this.http = useService("http");
        this.ui = useService("ui");

        this.fileInput = useRef("fileInput");
    }

    triggerFileInput() {
        this.fileInput.el.click();
    }

    handleFileChange(ev) {
        const file = ev.target.files[0];
        this.loadImage(file);
    }

    handleDrop(ev) {
        ev.preventDefault();
        this.state.dragging = false;
        const file = ev.dataTransfer.files[0];
        this.loadImage(file);
    }

    loadImage(file) {
        if (file && file.type.startsWith("image/")) {
            this.state.imageFile = file;
            const reader = new FileReader();
            reader.onload = (e) => {
                this.state.previewData = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    }

    async handleSearch() {
        if (!this.state.imageFile) {
            console.warn("No image selected");
            return;
        }

        const formData = new FormData();
        formData.append("image", this.state.imageFile);

        try {
            this.ui.block();
            const response = await this.http.post("/image_search/", {
                image: this.state.imageFile,
            }, "text");
            const data = JSON.parse(response);
            this.ui.unblock();
            if (data.product_ids){
                window.location.href = `/shop?product_ids=${JSON.stringify(data.product_ids)}`;
            }
        } catch (error) {
            console.error("Image search failed:", error);
        }
    }
}
