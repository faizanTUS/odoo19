/** @odoo-module **/
import { Dialog } from "@web/core/dialog/dialog";
import { Component, useState, onWillStart, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

export class MergePdfDialog extends Component {
    static template = "pdf_split_and_merge.MergePdfDialog";
    static components = { Dialog };
    static props = {
        '*': true,
        documentId: { type: Number, optional: true },
    };

    setup() {
        this.notification = useService("notification");
        this.action = useService("action");
        this.dialog = useService("dialog");
        this.state = useState({
            pageOrder: [],
            selectedPages: new Set(),
            isLoading: true,
            error: null,
            fileUpload: null,
            nextPageNumber: 1
        });

        this.dropZoneRef = useRef("dropZone");
        this.fileInputRef = useRef("fileInput");

        onWillStart(async () => {
            await this.loadData();
        });
    }

    closeDialog() {
        this.action.doAction({ type: "ir.actions.act_window_close" });
    }

    onCheckboxClick(ev, index) {
        ev.preventDefault();
        ev.target.checked = !ev.target.checked;
        this.togglePageSelection(index);
    }

    togglePageSelection(index) {
        const newSelection = new Set(this.state.selectedPages);
        if (newSelection.has(index)) {
            newSelection.delete(index);
        } else {
            newSelection.add(index);
        }
        this.state.selectedPages = newSelection;
    }

    triggerFileInput() {
        this.fileInputRef.el.click();
    }

    handleDragStart = (e, index) => {
        e.dataTransfer.setData('text/plain', index.toString());
    };

    handleDragOver = (e) => {
        e.preventDefault();
    };

    handleDrop = (e, targetIndex) => {
        e.preventDefault();
        const sourceIndex = parseInt(e.dataTransfer.getData('text/plain'));
        if (isNaN(sourceIndex)) return;

        const item = this.state.pageOrder[sourceIndex];
        this.state.pageOrder.splice(sourceIndex, 1);
        this.state.pageOrder.splice(targetIndex, 0, item);
    };

    async loadData() {
        try {
            const result = await rpc("/pdf_merge/load_data", {
                document_id: this.props.action.props.documentId,
            });

            if (result.error) {
                this.state.error = result.error;
            } else {
                const originalPages = result.original_pages.map(p => ({
                    type: 'original',
                    id: `original_${p.number}`,
                    page_number: p.number,
                    preview_url: p.preview_url,
                    content: null
                }));

                const splitPages = result.split_files.map(p => ({
                    type: 'split',
                    id: p.id,
                    name: p.name,
                    page_number: p.page_number,
                    preview_url: p.preview_url,
                    content: null
                }));

                this.state.pageOrder = [...originalPages, ...splitPages];

                if (this.state.pageOrder.length > 0) {
                    const maxPageNumber = Math.max(
                        ...this.state.pageOrder.map(p => p.page_number)
                    );
                    this.state.nextPageNumber = maxPageNumber + 1;
                } else {
                    this.state.nextPageNumber = 1;
                }

                this.state.selectedPages = new Set(
                    Array.from({length: this.state.pageOrder.length}, (_, i) => i)
                );
            }
        } catch (error) {
            this.state.error = "Failed to load PDF data";
            console.error("Error:", error);
        } finally {
            this.state.isLoading = false;
        }
    }

    async onFileUpload(e) {
        const files = e.target.files;
        if (files.length === 0) return;

        const file = files[0];
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            this.notification.add("Please upload only PDF files", { type: "warning" });
            this.fileInputRef.el.value = '';
            return;
        }
        const reader = new FileReader();

        reader.onload = async (e) => {
            try {
                const result = await rpc("/pdf_merge/process_uploaded_file", {
                    file_name: file.name,
                    file_content: e.target.result.split(',')[1],
                    document_id: this.props.action.props.documentId,
                    start_page: this.state.nextPageNumber
                });

                if (result.error) {
                    this.notification.add(result.error, { type: "danger" });
                    return;
                }

                const currentLength = this.state.pageOrder.length;
                result.pages.forEach(page => {
                    this.state.pageOrder.push({
                        type: 'uploaded',
                        id: page.id,
                        name: file.name,
                        page_number: page.number,
                        preview_url: page.preview_url,
                        content: page.content
                    });
                });

                this.state.nextPageNumber += result.pages.length;

                const newSelection = new Set(this.state.selectedPages);
                for (let i = 0; i < result.pages.length; i++) {
                    newSelection.add(currentLength + i);
                }
                this.state.selectedPages = newSelection;

                this.fileInputRef.el.value = '';
            } catch (error) {
                this.notification.add("Failed to process PDF file: " + error.message, { type: "danger" });
                console.error("File upload error:", error);
            }
        };
        reader.onerror = () => {
            this.notification.add("Error reading file", { type: "danger" });
        };
        reader.readAsDataURL(file);
    }

    async mergePages() {
        if (this.state.selectedPages.size === 0) {
            this.notification.add("Please select at least one page to merge", { type: "warning" });
            return;
        }

        const selectedPages = [];
        this.state.pageOrder.forEach((page, index) => {
            if (this.state.selectedPages.has(index)) {
                selectedPages.push({
                    type: page.type,
                    id: page.id,
                    page_number: page.page_number,
                    content: page.content
                });
            }
        });

        try {
            const pagesWithContent = await Promise.all(
                selectedPages.map(async (page) => {
                    if (page.content) return page;

                    const result = await rpc("/pdf_merge/get_page_content", {
                        document_id: this.props.action.props.documentId,
                        page_id: page.id,
                        page_type: page.type,
                        page_number: page.page_number
                    });

                    if (result.error) throw new Error(result.error);
                    return {
                        ...page,
                        content: result.content
                    };
                })
            );

            const result = await rpc("/pdf_merge/merge_pages", {
                document_id: this.props.action.props.documentId,
                pages: pagesWithContent
            });

            if (result.success) {
                this.notification.add("PDF merged successfully", { type: "success" });
                this.action.doAction({ type: "ir.actions.act_window_close" });
            } else {
                this.notification.add(result.error || "Merge failed", { type: "danger" });
            }
        } catch (error) {
            this.notification.add("Error during merge: " + error.message, { type: "danger" });
            console.error("Merge error:", error);
        }
    }
}

registry.category("actions").add("open_merge_pdf_dialog", MergePdfDialog);
