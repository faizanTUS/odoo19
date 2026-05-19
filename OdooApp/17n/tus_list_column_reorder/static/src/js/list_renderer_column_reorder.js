/** @odoo-module **/

import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { onMounted, onPatched, onWillUnmount } from "@odoo/owl";

const originalGetActiveColumns = ListRenderer.prototype.getActiveColumns;

// Build unique key for each list view across all modules
function tusBuildViewKey(renderer, list) {
    const props = renderer.props || {};
    const archInfo = props.archInfo || {};
    const lst = list || props.list || {};

    // Extract view ID from multiple possible sources
    const viewId =
        archInfo.id ||
        archInfo.viewId ||
        archInfo.view_id ||
        (props.context && props.context.tree_view_ref) ||
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

    // 2. Try config
    if (!model && lst.config) {
        model = lst.config.resModel || lst.config.model || null;
    }

    // 3. Try archInfo
    if (!model) {
        model = archInfo.model || archInfo.resModel || null;
    }

    // 4. Try props directly
    if (!model && props.resModel) {
        model = props.resModel;
    }

    // 5. Try context
    if (!model && props.context && props.context.active_model) {
        model = props.context.active_model;
    }

    const archHash =
        archInfo.archHash ||
        archInfo.arch_hash ||
        null;

    // Create a composite key that includes action context if available
    const actionId = props.context?.active_id || null;

    return { viewId, model, archHash, actionId };
}

patch(ListRenderer.prototype, {
    // ------------------------------------------------------------
    // Lifecycle
    // ------------------------------------------------------------
    setup() {
        super.setup(...arguments);

        this.orm = useService("orm");
        this.notification = useService("notification");

        this._tus_defaultColumns = null;
        this._tus_columnsInitialized = false;
        this._tus_fieldOrder = null;
        this._tus_mouseDownColumnName = null;
        this._tus_dragStartX = null;
        this._tus_dragStartY = null;
        this._tus_isDragging = false;

        // view/model info + flag to avoid multiple RPCs
        this._tus_viewKey = null;
        this._tus_viewKeyComputed = false;
        this._tus_orderLoaded = false;

        onMounted(() => {
            this._tus_computeViewKey();
            this._tus_installHeaderEnhancements();
        });

        onPatched(() => {
            this._tus_installHeaderEnhancements();
        });

        onWillUnmount(() => {
            // Cleanup document event listener
            if (this._tus_boundMouseUp) {
                document.removeEventListener("mouseup", this._tus_boundMouseUp);
                this._tus_boundMouseUp = null;
            }
        });
    },

    // ------------------------------------------------------------
    // View key computation
    // ------------------------------------------------------------
    _tus_computeViewKey() {
        if (!this._tus_viewKeyComputed) {
            this._tus_viewKey = tusBuildViewKey(this, this.props.list);
            this._tus_viewKeyComputed = true;
        }
    },

    // ------------------------------------------------------------
    // Column logic (load order from database)
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

        // Compute view key first (before anything else)
        this._tus_computeViewKey();

        // first time: capture defaults
        if (!this._tus_columnsInitialized) {
            this._tus_defaultColumns = columns.slice();
            this._tus_columnsInitialized = true;
        }

        // lazy-load saved order exactly once per view
        if (!this._tus_orderLoaded) {
            this._tus_orderLoaded = true;

            const { viewId, model, archHash } = this._tus_viewKey || {};
            if (!model) {
                console.warn(
                    "[TUS] Cannot load order - model not found:",
                    this._tus_viewKey
                );
                this.columns = columns;
                return columns;
            }


            // Use promise to load order synchronously during first render
            this.env.services.orm
                .call(
                    "ir.ui.view.column.order",
                    "get_order",
                    [viewId || false, model, archHash || false],
                    {}
                )
                .then((order) => {
                    if (Array.isArray(order) && order.length > 0) {
                        this._tus_fieldOrder = order;
                        // Force component update to apply the saved order
                        if (this.env.model && this.env.model.load) {
                            this.env.model.load();
                        }
                    } else {
                        this._tus_fieldOrder = null;
                    }
                })
                .catch((e) => {
                    console.error("[TUS] Failed to load saved order for", model, ":", e);
                    this._tus_fieldOrder = null;
                });
        }

        // apply saved order if present
        const order = this._tus_fieldOrder;
        if (!order || !order.length) {
            this.columns = columns;
            return columns;
        }

        // Build map of columns by name
        const byName = {};
        for (const col of columns) {
            if (col.name) {
                byName[col.name] = col;
            }
        }

        // Apply saved order
        const ordered = [];
        for (const name of order) {
            if (byName[name]) {
                ordered.push(byName[name]);
                delete byName[name];
            }
        }
        // Add any columns not in saved order (new fields added after)
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

            // Make the entire th draggable
            th.dataset.tusColumnName = fieldName;

            if (th.dataset.tusMouseBound === "1") {
                return;
            }
            th.dataset.tusMouseBound = "1";

            // Add visual feedback with move cursor
            th.style.cursor = "move";
            th.title = "Click and drag to reorder columns";

            // Also apply move cursor to all children elements
            const allChildren = th.querySelectorAll("*");
            allChildren.forEach(child => {
                child.style.cursor = "move";
            });

            // Add hover effect
            th.addEventListener("mouseenter", () => {
                th.style.backgroundColor = "rgba(0, 123, 255, 0.05)";
            });
            th.addEventListener("mouseleave", () => {
                th.style.backgroundColor = "";
            });

            // Use proper event listeners with proper binding
            th.addEventListener("mousedown", (ev) => {
                // Only trigger drag if not clicking on dropdown or other buttons
                if (ev.target.closest("button, .dropdown, .o_optional_columns_dropdown")) {
                    return;
                }
                this._tus_onHeaderMouseDown(ev);
            });

            // Add document-level mouseup to catch all cases
            if (!this._tus_boundMouseUp) {
                this._tus_boundMouseUp = (ev) => {
                    if (this._tus_mouseDownColumnName) {
                        this._tus_onHeaderMouseUp(ev);
                    }
                };
                document.addEventListener("mouseup", this._tus_boundMouseUp);
            }
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
        span.innerHTML = "↻";
        span.style.cssText = "cursor: pointer; font-size: 16px; font-weight: bold; padding: 0 5px;";
        span.title = "Reset column order to default";

        // Ensure event listener is properly bound
        span.addEventListener("click", (ev) => {
            ev.stopPropagation();
            ev.preventDefault();
            this.tusOnResetColumnOrder(ev);
        }, true); // Use capture phase

        container.insertBefore(span, dropdownBtn);
    },

    // ------------------------------------------------------------
    // Drag logic
    // ------------------------------------------------------------
    _tus_onHeaderMouseDown(ev) {
        ev.preventDefault();
        ev.stopPropagation();

        const el = ev.currentTarget;
        const name = el && el.dataset.tusColumnName;
        this._tus_mouseDownColumnName = name || null;
        this._tus_dragStartX = ev.clientX;
        this._tus_dragStartY = ev.clientY;
        this._tus_isDragging = false;

    },

    async _tus_onHeaderMouseUp(ev) {
        if (!this._tus_mouseDownColumnName) {
            return;
        }

        // Find the column header under the mouse
        const el = document.elementFromPoint(ev.clientX, ev.clientY);
        if (!el) {
            this._tus_mouseDownColumnName = null;
            return;
        }

        // Find the closest th element
        const th = el.closest("th");
        const targetName = th ? (th.dataset.name || th.getAttribute("data-name")) : null;
        const sourceName = this._tus_mouseDownColumnName;

        this._tus_mouseDownColumnName = null;
        this._tus_isDragging = false;


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

        // Force proper re-render
        if (this.env.model && this.env.model.load) {
            this.env.model.load();
        }
    },

    async _tus_persistColumnOrder() {
        const key = this._tus_viewKey || {};
        const { viewId, model, archHash } = key;
        const order = this._tus_fieldOrder || [];

        if (!model) {
            console.warn(
                "[TUS] Cannot save order - missing model:",
                key
            );
            return;
        }


        try {
            await this.env.services.orm.call(
                "ir.ui.view.column.order",
                "set_order",
                [viewId || false, model, order, archHash || false],
                {}
            );

            // Show success notification

        } catch (error) {
            console.error("[TUS] Failed to save column order:", error);
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
            this.notification.add("No default column order available", {
                type: "info",
            });
            return;
        }

        const key = this._tus_viewKey || {};
        const { viewId, model, archHash } = key;

        if (!model) {
            console.warn(
                "[TUS] Cannot reset - missing model:",
                key
            );
            return;
        }

        if (!window.confirm("Reset column order to default?")) {
            return;
        }

        try {
            // Delete saved order by passing empty array
            await this.env.services.orm.call(
                "ir.ui.view.column.order",
                "set_order",
                [viewId || false, model, [], archHash || false],
                {}
            );

            this._tus_fieldOrder = null;
            this.columns = this._tus_defaultColumns.slice();


            // Force proper re-render
            if (this.env.model && this.env.model.load) {
                this.env.model.load();
            }

            this.notification.add("Column order reset to default", {
                type: "success",
            });
        } catch (error) {
            console.error("[TUS] Failed to reset column order:", error);
            this.notification.add("Could not reset column order", {
                type: "warning",
            });
        }
    },
});