/** @odoo-module **/

import { session } from "@web/session";

/** Set after a successful ``rules_payload_for_user`` RPC; ``undefined`` = use session only. */
let _liveRules = undefined;
let _refreshPromise = null;

function rulesFromSession() {
    try {
        const raw = session.aac_rules_json;
        if (!raw) {
            return { empty: true };
        }
        return typeof raw === "string" ? JSON.parse(raw) : raw;
    } catch {
        return { empty: true };
    }
}

/**
 * Load current user's rules from the server (fresh; not the login-time session snapshot).
 * Safe to call from ``onWillStart`` on list/form controllers.
 */
export function refreshAacRules(orm) {
    _refreshPromise = (async () => {
        try {
            const raw = await orm.call("advanced.access.service", "rules_payload_for_user", []);
            _liveRules = typeof raw === "string" ? JSON.parse(raw) : raw;
        } catch {
            _liveRules = undefined;
        }
    })();
    return _refreshPromise;
}

/**
 * Ensures rules have been refreshed at least once this session/component life.
 */
export async function ensureAacRules(orm) {
    if (_liveRules === undefined) {
        if (_refreshPromise) {
            await _refreshPromise;
        } else if (orm) {
            await refreshAacRules(orm);
        }
    }
    return aacRules();
}

/**
 * Parsed Advanced Access Control payload: prefers live RPC result, else ``aac_rules_json`` from session.
 */
export function aacRules() {
    if (_liveRules !== undefined) {
        return _liveRules;
    }
    return rulesFromSession();
}

/**
 * Effective UI caps for a model: merges per-model lines with global import/export/archive toggles.
 * @param {string} resModel
 * @returns {Record<string, boolean>|null}
 */
export function aacModelUi(resModel) {
    const rules = aacRules();
    if (rules.empty || !resModel) {
        return null;
    }
    const caps = rules.model_ui && rules.model_ui[resModel];
    const merged = {
        create: caps ? caps.create !== false : true,
        write: caps ? caps.write !== false : true,
        unlink: caps ? caps.unlink !== false : true,
        export: caps ? caps.export !== false : true,
        duplicate: caps ? caps.duplicate !== false : true,
        import: caps ? caps.import !== false : true,
        archive: caps ? caps.archive !== false : true,
    };
    if (rules.global_disable_import) {
        merged.import = false;
    }
    if (rules.global_disable_export) {
        merged.export = false;
    }
    if (rules.global_disable_archive) {
        merged.archive = false;
    }
    return merged;
}

/**
 * Report action ids (ir.actions.report) hidden from Print for this model.
 * @param {string} resModel
 * @returns {number[]}
 */
export function aacHiddenReportIds(resModel) {
    const rules = aacRules();
    if (rules.empty || !resModel) {
        return [];
    }
    const m = rules.hidden_reports_by_model && rules.hidden_reports_by_model[resModel];
    return Array.isArray(m) ? m : [];
}

/**
 * ``ir.actions.actions`` ids to remove from the list Actions menu (sidebar bindings).
 * @param {string} resModel
 * @returns {number[]}
 */
export function aacHiddenSidebarActionIds(resModel) {
    const rules = aacRules();
    if (rules.empty || !resModel) {
        return [];
    }
    const m =
        rules.hidden_sidebar_action_ids_by_model &&
        rules.hidden_sidebar_action_ids_by_model[resModel];
    return Array.isArray(m) ? m : [];
}

/**
 * Robustly extract a numeric ID from a sidebar menu item (Odoo 17 format).
 * @param {object} item
 * @returns {number|null}
 */
export function extractActionId(item) {
    if (!item) return null;
    // Direct action object ID
    if (item.action && typeof item.action.id === "number") {
        return item.action.id;
    }
    // item.key can be "action_server_327" or similar
    if (typeof item.key === "string" && item.key.includes("_")) {
        const parts = item.key.split("_");
        const last = parts[parts.length - 1];
        if (/^\d+$/.test(last)) {
            return parseInt(last);
        }
    }
    // Fallback to direct key or id if they are numbers
    if (typeof item.key === "number") return item.key;
    if (typeof item.id === "number") return item.id;
    return null;
}
