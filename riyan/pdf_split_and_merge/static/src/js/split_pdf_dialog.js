/** @odoo-module **/
import { Dialog } from "@web/core/dialog/dialog";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

export class SplitPdfDialog extends Component {
    static template = "pdf_split_and_merge.SplitPdfDialog";
    static components = { Dialog };

    setup() {
        this.notification = useService("notification");
        this.state = useState({
            pages: [],
            selected: new Set(),
            isLoading: true,
            error: null
        });
        this.action = useService("action");
        this.toggleSelection = this.toggleSelection.bind(this);

        onWillStart(async () => {
            try {
                const result = await rpc("/pdf_split/load_pages", {
                    document_id: this.props.action.props.documentId,
                });

                if (result.error) {
                    this.state.error = result.error;
                } else {
                    this.state.pages = result.pages;
                    result.pages.forEach(p => this.state.selected.add(p.number));
                }
            } catch (error) {
                this.state.error = "Failed to load PDF pages";
                console.error("Error:", error);
            } finally {
                this.state.isLoading = false;
            }
        });
    }

    closeDialog() {
        this.action.doAction({ type: "ir.actions.act_window_close" });
    }

    onCheckboxClick = (ev, pageNum) => {
        ev.preventDefault();
        ev.target.checked = !ev.target.checked;
        this.toggleSelection(pageNum);
    }

    toggleSelection(pageNum) {
        if (this.state.selected.has(pageNum)) {
            this.state.selected.delete(pageNum);
        } else {
            this.state.selected.add(pageNum);
        }
    }

    async splitSelectedPages() {
        if (this.state.selected.size === 0) {
            this.notification.add("Please select at least one page to split.", { type: "warning"});
            return;
        }
        const selected = [...this.state.selected];

        const result = await rpc("/pdf_split/split_selected", {
            document_id: this.props.action.props.documentId,
            selected_pages: selected,
        });

        if (result.success) {
            this.notification.add("PDF Split successful", { type: "success" });
            this.action.doAction({ type: "ir.actions.act_window_close" });
        } else {
            this.notification.add("Split failed", { type: "danger" });
        }
    }
}
registry.category("actions").add("open_split_pdf_dialog", SplitPdfDialog);
