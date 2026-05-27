/** @odoo-module **/

import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { onMounted, onPatched } from "@odoo/owl";

// keep original references
const originalSetup = ListRenderer.prototype.setup;
const originalGetActiveColumns = ListRenderer.prototype.getActiveColumns;

// Build key from renderer + list
function tusBuildViewKey(renderer, list) {
    const props = renderer.props || {};
    const archInfo = props.archInfo || {};
    const lst = list || props.list || {};

    const viewId =
        archInfo.id ||
        archInfo.viewId ||
        archInfo.view_id ||
        null;

    let model = null;

    // 1. Try list.model (RelationalModel)
    if (lst && lst.model) {
        const lm = lst.model;
        if (typeof lm === "string") {
            model = lm;
        } else {
            model =
                lm.resModel ||
                lm.modelName ||
                lm.model ||
                lm.name ||
                null;
        }
    }

    // 2. Fallbacks
    if (!model) {
        model =
            archInfo.model ||
            (lst.config && lst.config.resModel) ||
            null;
    }

    const archHash =
        archInfo.archHash ||
        archInfo.arch_hash ||
        null;

    return { viewId, model, archHash };
}

patch(ListRenderer.prototype, {
    // ------------------------------------------------------------
    // Lifecycle
    // ------------------------------------------------------------
    setup() {

        if (originalSetup) {
            originalSetup.apply(this, arguments);
        }

        this.orm = useService("orm");
        this.notification = useService("notification");

        this._tus_defaultColumns = null;
        this._tus_columnsInitialized = false;
        this._tus_fieldOrder = null;
        this._tus_mouseDownColumnName = null;

        // view/model info + flag to avoid multiple RPCs
        this._tus_viewKey = null;
        this._tus_viewKeyComputed = false;
        this._tus_orderLoaded = false;

        onMounted(() => {
            // just for DOM enhancements. no RPC here.
            this._tus_installHeaderEnhancements();
        });
        onPatched(() => {
            this._tus_installHeaderEnhancements();
        });
    },

    // ------------------------------------------------------------
    // Column logic (load order from here)
    // ------------------------------------------------------------
    getActiveColumns(list) {
        let columns;
        if (originalGetActiveColumns) {
            columns = originalGetActiveColumns.call(this, list);
        } else {
            columns = this.columns || [];
        }

        if (!columns || !columns.length) {
            this.columns = columns;
            return columns;
        }

        // first time: capture defaults
        if (!this._tus_columnsInitialized) {
            this._tus_defaultColumns = columns.slice();
            this._tus_columnsInitialized = true;
        }

        // first time we know list. compute view key
        if (!this._tus_viewKeyComputed) {
            this._tus_viewKey = tusBuildViewKey(this, list);
            this._tus_viewKeyComputed = true;
        }

        // lazy-load saved order exactly once. now we are SURE we have list+model.
        if (!this._tus_orderLoaded) {
            this._tus_orderLoaded = true;

            const { viewId, model, archHash } = this._tus_viewKey || {};
            if (!model) {
                console.warn(
                    "TUS v18: cannot load order. model not found",
                    this._tus_viewKey
                );
            } else {
                this.orm
                    .call(
                        "ir.ui.view.column.order",
                        "get_order",
                        [viewId || false, model, archHash || false],
                        {}
                    )
                    .then((order) => {
                        if (Array.isArray(order) && order.length) {
                            this._tus_fieldOrder = order;
                            this.render(); // trigger re-call of getActiveColumns with order applied
                        }
                    })
                    .catch((e) => {
                        console.error("TUS v18: get_order failed", e);
                    });
            }
        }

        // apply saved order if present
        const order = this._tus_fieldOrder;
        if (!order || !order.length) {
            this.columns = columns;
            return columns;
        }

        const byName = {};
        for (const col of columns) {
            if (col.name) {
                byName[col.name] = col;
            }
        }

        const ordered = [];
        for (const name of order) {
            if (byName[name]) {
                ordered.push(byName[name]);
                delete byName[name];
            }
        }
        for (const leftover in byName) {
            ordered.push(byName[leftover]);
        }

        this.columns = ordered;
        return ordered;
    },

    // ------------------------------------------------------------
    // DOM enhancements: drag + reset icon before dropdown
    // ------------------------------------------------------------
    _tus_installHeaderEnhancements() {
        if (!this.columns || !this.columns.length) {
            return;
        }

        let root = (this.tableRef && this.tableRef.el) || null;
        if (!root && this.el) {
            root = this.el.querySelector("table.o_list_table");
        }
        if (!root) {
            return;
        }

        const thead = root.querySelector("thead");
        if (!thead) {
            return;
        }

        const headers = thead.querySelectorAll("th");
        if (!headers.length) {
            return;
        }

        const colByName = {};
        this.columns.forEach((c) => {
            if (c.name) {
                colByName[c.name] = c;
            }
        });

        // bind drag by header
        headers.forEach((th) => {
            const fieldName = th.dataset.name || th.getAttribute("data-name");
            if (!fieldName || !colByName[fieldName]) {
                return; // ignore checkbox, etc.
            }

            let handle =
                th.querySelector(".o_column_sortable") ||
                th.querySelector("button, span, div") ||
                th;

            handle.dataset.tusColumnName = fieldName;

            if (handle.dataset.tusMouseBound === "1") {
                return;
            }
            handle.dataset.tusMouseBound = "1";
            handle.style.cursor = "move";

            handle.addEventListener("mousedown", (ev) =>
                this._tus_onHeaderMouseDown(ev)
            );
            handle.addEventListener("mouseup", (ev) =>
                this._tus_onHeaderMouseUp(ev)
            );
        });

        this._tus_installResetBeforeDropdown(thead);
    },

    _tus_installResetBeforeDropdown(thead) {
        if (thead.querySelector(".o_tus_reset_columns")) {
            return;
        }

        const dropdownBtn =
            thead.querySelector(
                ".o_optional_columns_dropdown_toggler, " +
                    ".o_optional_columns_dropdown_toggle, " +
                    "th button.dropdown-toggle"
            );

        if (!dropdownBtn) {
            return;
        }

        const container = dropdownBtn.parentNode;
        if (!container) {
            return;
        }

        const span = document.createElement("span");
        span.className = "o_tus_reset_columns me-1";
        span.textContent = "↻";
        span.style.cursor = "pointer";
        span.title = "Reset column order to default";

        span.addEventListener("click", (ev) => this.tusOnResetColumnOrder(ev));

        container.insertBefore(span, dropdownBtn);
    },

    // ------------------------------------------------------------
    // Drag logic
    // ------------------------------------------------------------
    _tus_onHeaderMouseDown(ev) {
        const el = ev.currentTarget;
        const name = el && el.dataset.tusColumnName;
        this._tus_mouseDownColumnName = name || null;
    },

    async _tus_onHeaderMouseUp(ev) {
        const el = ev.currentTarget;
        const targetName = el && el.dataset.tusColumnName;
        const sourceName = this._tus_mouseDownColumnName;
        this._tus_mouseDownColumnName = null;

        if (!sourceName || !targetName || sourceName === targetName) {
            return;
        }
        if (!this.columns || !this.columns.length) {
            return;
        }

        if (!this._tus_fieldOrder || !this._tus_fieldOrder.length) {
            this._tus_fieldOrder = this.columns
                .map((c) => c.name)
                .filter((n) => !!n);
        }

        const fromIndex = this._tus_fieldOrder.indexOf(sourceName);
        const toIndex = this._tus_fieldOrder.indexOf(targetName);
        if (fromIndex < 0 || toIndex < 0) {
            return;
        }

        const order = this._tus_fieldOrder.slice();
        const moved = order.splice(fromIndex, 1)[0];
        order.splice(toIndex, 0, moved);
        this._tus_fieldOrder = order;


        await this._tus_persistColumnOrder();
        this.render();
    },

    async _tus_persistColumnOrder() {
        const key = this._tus_viewKey || {};
        const { viewId, model, archHash } = key;
        const order = this._tus_fieldOrder || [];

        if (!model) {
            console.warn(
                "TUS Column Reorder: cannot save order. missing model",
                key
            );
            return;
        }


        try {
            await this.orm.call(
                "ir.ui.view.column.order",
                "set_order",
                [viewId || false, model, order, archHash || false],
                {}
            );
        } catch (error) {
            console.error("TUS Column Reorder: Failed to persist order", error);
            this.notification.add("Could not save column order", {
                type: "warning",
            });
        }
    },

    // ------------------------------------------------------------
    // Reset handler
    // ------------------------------------------------------------
    async tusOnResetColumnOrder(ev) {
        if (ev) {
            ev.stopPropagation();
            ev.preventDefault();
        }

        if (!this._tus_defaultColumns) {
            return;
        }

        if (!window.confirm("Reset column order to default for this view?")) {
            return;
        }

        const key = this._tus_viewKey || {};
        const { viewId, model, archHash } = key;

        if (!model) {
            console.warn(
                "TUS Column Reorder: cannot reset. missing model",
                key
            );
            return;
        }

        try {
            await this.orm.call(
                "ir.ui.view.column.order",
                "set_order",
                [viewId || false, model, [], archHash || false],
                {}
            );

            this._tus_fieldOrder = null;
            this.columns = this._tus_defaultColumns.slice();
            this.render();

            this.notification.add("Column order reset to default", {
                type: "success",
            });
        } catch (error) {
            console.error("TUS Column Reorder: Failed to reset order", error);
            this.notification.add("Could not reset column order", {
                type: "warning",
            });
        }
    },
});
