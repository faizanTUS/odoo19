/** @odoo-module **/
import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";
//import { patch } from 'web.utils';
import { useService, useBus } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";
import { whenReady } from "@odoo/owl";

whenReady(() => {
    patch(ListRenderer.prototype, 'odoo_split_view/static/src/js/split_controller_panel.js', {
        setup() {
    //        super.setup();
            this._super();
            this.split = useService("splitView");
            this.st = useState(this.split.state);
            this.orm = useService("orm");
            this.action = useService("action");
            this.syncInterval = null;

            useBus(this.env.bus, "split_view_update", () => {
                setTimeout(() => this.setupSplitPanel(), 50);
            });
        },

        setupSplitPanel() {
            this.nuclearCleanup();

            if (this.st.active) {
                setTimeout(() => {
                    this.createRightPanel();
                    this.startListSync(); // Start real-time sync
                }, 100);
            } else {
                this.stopListSync(); // Stop sync when split off
            }
        },

        // Real-time list synchronization
        startListSync() {
            if (this.st.active && !this.syncInterval) {
                this.syncInterval = setInterval(async () => {
                    if (this.st.active) {
                        try {
                            await this.env.services.action.doAction({
                                type: 'ir.actions.client',
                                tag: 'soft_reload'
                            });
                        } catch (error) {
                            if (this.props.list && this.props.list.model) {
                                await this.props.list.model.root.load();
                                this.render();
                            }
                        }
                    }
                }, 5000);
            }
        },

        stopListSync() {
            if (this.syncInterval) {
                clearInterval(this.syncInterval);
                this.syncInterval = null;
            }
        },

        nuclearCleanup() {
            document.body.classList.remove(
                'o_split_active',
                'o_split_vertical',
                'o_split_horizontal',
                'split_fullscreen'
            );

            const selectors = [
                '.o_split_form_panel',
                '#right_panel',
                '[id*="split"]',
                '[id*="panel"]',
                '[class*="split"]'
            ];

            selectors.forEach(selector => {
                document.querySelectorAll(selector).forEach(el => {
                    if (el.id.includes('panel') || el.classList.contains('o_split_form_panel')) {
                        el.remove();
                    }
                });
            });

            document.querySelectorAll('.o_split_selected').forEach(r => r.classList.remove('o_split_selected'));
        },

        createRightPanel() {

            const existing = document.getElementById('right_panel');
            if (existing) existing.remove();

            document.body.classList.add("o_split_active", `o_split_${this.st.direction}`);

            const panel = document.createElement('div');
            panel.id = 'right_panel';
            panel.className = "o_split_form_panel";

            panel.innerHTML = `
                <div class="o_split_resize_handle" id="split_resizer"></div>
                <div class="o_split_content" id="form_wrapper" style="width: 100%; height: 100%;overflow-x: auto !important;">
                    <div id="form_container" style="height:100%;padding:0;"></div>
                </div>
            `;

            document.body.appendChild(panel);

            // Resize Logic for both panels
            const resizer = document.getElementById("split_resizer");
            const formWrapper = document.getElementById("form_wrapper");
            const leftPanel = document.querySelector(".o_content");

            let isResizing = false;

            resizer.addEventListener("mousedown", function (e) {
                isResizing = true;
                document.body.style.userSelect = "none";
                document.body.style.cursor =
                    document.body.classList.contains("o_split_horizontal") ? "ns-resize" : "ew-resize";
            });

            window.addEventListener("mousemove", function (e) {
                if (!isResizing) return;

                if (document.body.classList.contains("o_split_vertical")) {
                    const totalWidth = window.innerWidth;
                    const newRightWidth = totalWidth - e.clientX;
                    const newLeftWidth = e.clientX;

                    formWrapper.style.width = `${newRightWidth}px`;
                    if (leftPanel) {
                        leftPanel.style.width = `${newLeftWidth}px`;
                    }
                }

                if (document.body.classList.contains("o_split_horizontal")) {
                    const totalHeight = window.innerHeight;
                    const newBottomHeight = totalHeight - e.clientY;
                    const topPanel = document.querySelector(".o_content");

                    formWrapper.style.height = `${newBottomHeight}px`;
                    if (topPanel) {
                        topPanel.style.height = `${e.clientY - 96}px`; // 96px for header & control panel
                    }
                }
            });

            window.addEventListener("mouseup", function () {
                if (isResizing) {
                    isResizing = false;
                    document.body.style.userSelect = "";
                    document.body.style.cursor = "";
                }
            });

        },

        async onCellClicked(record, column, ev) {
            if (this.st && this.st.active) {
                const realRecordId = record.resId || record.data?.id || record.id;
                if (!realRecordId) {
                    console.error("Could not extract record ID");
                    return;
                }
                await this.openFullFormInRightPanel(realRecordId);
                document.querySelectorAll('tr.o_data_row').forEach(r => r.classList.remove('o_split_selected'));
                const row = ev.target.closest('tr.o_data_row');
                if (row) row.classList.add('o_split_selected');
                return;
            }
            return super.onCellClicked(record, column, ev);
        },

//        async openFullFormInRightPanel(recordId) {
//            const model = this.props.list.resModel;
//            const formUrl = `/web#id=${recordId}&model=${model}&view_type=form`;
//            const iframe = document.createElement('iframe');
//            iframe.src = formUrl;
//            iframe.style.cssText = "width: 100%; height: 100%; border: none;";
//            const container = document.getElementById('form_container');
//            container.innerHTML = '';
//            container.appendChild(iframe);
//        }
        async openFullFormInRightPanel(recordId) {
            const model = this.props.list.resModel;
            const formUrl = `/web#id=${recordId}&model=${model}&view_type=form`;
            const iframe = document.createElement('iframe');
            iframe.src = formUrl;
            iframe.style.cssText = "width: 100%; height: 100%; border: none;";
            iframe.setAttribute("id", "dynamic_form_iframe");

            const container = document.getElementById('form_container');
            container.innerHTML = '';
            container.appendChild(iframe);

            // Wait for iframe to load, then remove header elements
            iframe.onload = function () {
                try {
                    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;

                    // Wait for Odoo to render full content
                    const interval = setInterval(() => {
                        const controlPanel = iframeDoc.querySelector('.o_control_panel');
                        const navbar = iframeDoc.querySelector('.o_main_navbar');

                        if (controlPanel || navbar) {
                            if (controlPanel) controlPanel.style.display = 'none';
                            if (navbar) navbar.style.display = 'none';
                            clearInterval(interval);
                        }
                    }, 300);
                } catch (err) {
                    console.error("Failed to access iframe content:", err);
                }
            };
        }
    });
});
