/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { ListController } from "@web/views/list/list_controller";
import { useEffect, useState } from "@odoo/owl";

function getAutoRefreshSession() {
    return (
        session.list_kanban_auto_refresh || {
            global_enabled: false,
            interval_ms: 10000,
        }
    );
}

function setupAutoRefresh(controller) {
    const cfg = getAutoRefreshSession();
    const globalOn = Boolean(cfg.global_enabled);
    controller.autoRefreshState = useState({
        enabled: globalOn,
    });
    controller._autoRefreshLoading = false;
    useEffect(
        () => {
            const intervalMs = Math.max(1000, getAutoRefreshSession().interval_ms || 10000);
            if (!controller.autoRefreshState.enabled) {
                return () => {};
            }
            const timerId = setInterval(() => controller._autoRefreshTick(), intervalMs);
            return () => clearInterval(timerId);
        },
        () => [controller.autoRefreshState.enabled]
    );
}

function toggleAutoRefresh(controller) {
    if (!getAutoRefreshSession().global_enabled) {
        return;
    }
    controller.autoRefreshState.enabled = !controller.autoRefreshState.enabled;
}

function getAutoRefreshClass(controller) {
    const base = "btn btn-sm o_list_kanban_auto_refresh ";
    return base + (controller.autoRefreshState.enabled ? "btn-primary" : "btn-secondary");
}

function getAutoRefreshTitle(controller) {
    const cfg = getAutoRefreshSession();
    const ms = Math.max(1000, cfg.interval_ms || 10000);
    if (!cfg.global_enabled) {
        return _t(
            "Auto refresh is disabled globally. Enable “Allow auto refresh data” in Settings → General Settings."
        );
    }
    return controller.autoRefreshState.enabled
        ? _t("Auto refresh is on (every %s ms). Click to pause for this view.", ms)
        : _t("Auto refresh is off. Click to enable for this view.");
}

async function autoRefreshTick(controller) {
    if (!controller.autoRefreshState.enabled) {
        return;
    }
    if (!getAutoRefreshSession().global_enabled) {
        return;
    }
    if (document.visibilityState === "hidden") {
        return;
    }
    if (controller.model?.root?.editedRecord) {
        return;
    }
    if (controller._autoRefreshLoading) {
        return;
    }
    controller._autoRefreshLoading = true;
    try {
        await controller.model.load();
    } catch {
        // Ignore background refresh errors (offline, access, etc.)
    } finally {
        controller._autoRefreshLoading = false;
    }
}

patch(ListController.prototype, "list_kanban_auto_refresh.ListController" ,{
    setup() {
        this._super(...arguments);
        setupAutoRefresh(this);
    },

    toggleListKanbanAutoRefresh() {
        toggleAutoRefresh(this);
    },

    getListKanbanAutoRefreshClass() {
        return getAutoRefreshClass(this);
    },

    getListKanbanAutoRefreshTitle() {
        return getAutoRefreshTitle(this);
    },

    getListKanbanAutoRefreshDisabled() {
        return !getAutoRefreshSession().global_enabled;
    },

    async _autoRefreshTick() {
        await autoRefreshTick(this);
    },
});

patch(KanbanController.prototype, "list_kanban_auto_refresh.KanbanController", {
    setup() {
        this._super(...arguments);
        setupAutoRefresh(this);
    },

    toggleListKanbanAutoRefresh() {
        toggleAutoRefresh(this);
    },

    getListKanbanAutoRefreshClass() {
        return getAutoRefreshClass(this);
    },

    getListKanbanAutoRefreshTitle() {
        return getAutoRefreshTitle(this);
    },

    getListKanbanAutoRefreshDisabled() {
        return !getAutoRefreshSession().global_enabled;
    },

    async _autoRefreshTick() {
        await autoRefreshTick(this);
    },
});
