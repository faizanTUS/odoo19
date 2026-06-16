/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { debounce } from "@web/core/utils/timing";
import { url } from "@web/core/utils/urls";
import { router } from "@web/core/browser/router";

import { Component, useState, useRef, onWillUnmount, onMounted } from "@odoo/owl";
import { usePopover } from "@web/core/popover/popover_hook";

const RECENT_STORAGE_KEY = "global_search_recent";
const FAVOURITES_STORAGE_KEY = "global_search_favourites";
const FREQUENT_STORAGE_KEY = "global_search_frequent";
const RECENT_MAX = 10;
const FAVOURITES_MAX = 30;
const FREQUENT_MAX = 20;
const FREQUENT_SHOW = 8;
const SEARCH_DEBOUNCE_MS = 300;

/**
 * Suggestion chips:
 * - `model` → browse recent records in that model (all contacts, all sale orders, …).
 * - `query` only → run text search (name_search) as before.
 */
export const SEARCH_SUGGESTIONS = [
    { label: "Contact", model: "res.partner" },
    /** Text-only search; only shown if `res.partner` is allowed when user restricts models. */
    { label: "Customer", query: "customer", relatedModels: ["res.partner"] },
    { label: "Sale Order", model: "sale.order" },
    { label: "Purchase Order", model: "purchase.order" },
    {
        label: "Customer Invoice",
        model: "account.move",
        browse_preset: "customer_invoices",
    },
    { label: "Product", model: "product.product" },
];

/**
 * Whether a suggestion chip applies to the user's Global Search Models whitelist.
 * @param {object} sug
 * @param {string[]|null|undefined} allowed technical names; empty = no models; null = config not loaded yet
 */
export function suggestionMatchesAllowedModels(sug, allowed) {
    if (allowed == null) {
        return false;
    }
    if (!allowed.length) {
        return false;
    }
    if (sug.model) {
        return allowed.includes(sug.model);
    }
    if (sug.query) {
        const rel = sug.relatedModels || ["res.partner"];
        return rel.some((m) => allowed.includes(m));
    }
    return false;
}

function escapeRegExp(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/**
 * Split display text into segments for keyword highlighting (query tokens, case-insensitive).
 */
export function getHighlightSegments(text, query) {
    const t = text ?? "";
    const tokens = (query || "")
        .trim()
        .split(/\s+/)
        .map((w) => w.trim())
        .filter((w) => w.length > 0);
    if (!tokens.length) {
        return [{ text: t, hl: false }];
    }
    const pattern = tokens.map((w) => escapeRegExp(w)).join("|");
    if (!pattern) {
        return [{ text: t, hl: false }];
    }
    const re = new RegExp(`(${pattern})`, "gi");
    const segments = [];
    let lastIndex = 0;
    let m;
    while ((m = re.exec(t)) !== null) {
        if (m.index > lastIndex) {
            segments.push({ text: t.slice(lastIndex, m.index), hl: false });
        }
        segments.push({ text: m[0], hl: true });
        lastIndex = m.index + m[0].length;
    }
    if (lastIndex < t.length) {
        segments.push({ text: t.slice(lastIndex), hl: false });
    }
    return segments.length ? segments : [{ text: t, hl: false }];
}

function getRecentSearches() {
    try {
        const raw = localStorage.getItem(RECENT_STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch {
        return [];
    }
}

function addRecentSearch(term) {
    term = (term || "").trim();
    if (term.length < 2) return;
    let recent = getRecentSearches();
    recent = [term, ...recent.filter((t) => t !== term)].slice(0, RECENT_MAX);
    try {
        localStorage.setItem(RECENT_STORAGE_KEY, JSON.stringify(recent));
    } catch {}
}

function getFavourites() {
    try {
        const raw = localStorage.getItem(FAVOURITES_STORAGE_KEY);
        const list = raw ? JSON.parse(raw) : [];
        return Array.isArray(list) ? list : [];
    } catch {
        return [];
    }
}

function saveFavourites(list) {
    try {
        localStorage.setItem(FAVOURITES_STORAGE_KEY, JSON.stringify(list.slice(0, FAVOURITES_MAX)));
    } catch {}
}

function getFrequentRecords() {
    try {
        const raw = localStorage.getItem(FREQUENT_STORAGE_KEY);
        const list = raw ? JSON.parse(raw) : [];
        return Array.isArray(list) ? list : [];
    } catch {
        return [];
    }
}

function saveFrequentRecords(list) {
    try {
        localStorage.setItem(FREQUENT_STORAGE_KEY, JSON.stringify(list.slice(0, FREQUENT_MAX)));
    } catch {}
}

function recordFrequentAccess(model, result) {
    let list = getFrequentRecords();
    const idx = list.findIndex((x) => x.model === model && x.id === result.id);
    const displayName = result.display_name || "";
    if (idx >= 0) {
        list[idx].count = (list[idx].count || 0) + 1;
        list[idx].lastAccess = Date.now();
        list[idx].display_name = displayName || list[idx].display_name;
    } else {
        list.push({
            model,
            id: result.id,
            display_name: displayName,
            count: 1,
            lastAccess: Date.now(),
        });
    }
    list.sort((a, b) => (b.count - a.count) || (b.lastAccess - a.lastAccess));
    list = list.slice(0, FREQUENT_MAX);
    saveFrequentRecords(list);
    return list;
}

function clearRecentSearches() {
    try {
        localStorage.removeItem(RECENT_STORAGE_KEY);
    } catch {}
}

/**
 * Odoo 18+ canonical URL for forms: /odoo/<model>/<id> (works in a new tab).
 * List views must use a real window action id (/odoo/action-<id>): model-only list URLs
 * depend on sessionStorage and are empty in a fresh tab.
 */
function urlToOpenRecordInNewTab(model, resId) {
    const base = router.current ? { ...router.current } : {};
    base.actionStack = [{ model, resId: Number(resId) }];
    return `${window.location.origin}${router.stateToUrl(base)}`;
}

export class GlobalSearchPanel extends Component {
    static template = "tus_smart_global_search.GlobalSearchPanel";
    static props = {
        close: { type: Function },
    };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.inputRef = useRef("input");
        this.panelRef = useRef("panel");

        this.state = useState({
            query: "",
            browseMode: false,
            browseModel: null,
            browsePreset: null,
            /** Filled from /config; empty list means no models selected (search/browse disabled). */
            allowedModels: [],
            /** False until the first successful /config response (avoids showing chips while unknown). */
            configLoaded: false,
            loading: false,
            error: false,
            groups: [],
            recentSearches: getRecentSearches(),
            favourites: getFavourites(),
            frequent: getFrequentRecords().slice(0, FREQUENT_SHOW),
            selectedIndex: 0,
        });

        // Stale-request guard: only the latest request's results are applied.
        this._reqId = 0;

        this._search = debounce(this.doSearch.bind(this), SEARCH_DEBOUNCE_MS);

        onMounted(async () => {
            setTimeout(() => this.inputRef.el?.focus(), 0);
            await this.loadConfigIfNeeded(false);
        });

        /** Full list; template uses filteredSuggestions */
        this.searchSuggestions = SEARCH_SUGGESTIONS;
    }

    /**
     * Load allowed models from the server. Use force=true before search/browse so we never run
     * with stale config (e.g. user cleared Global Search Models in another tab).
     * @param {boolean} force
     */
    async loadConfigIfNeeded(force = false) {
        if (!force && this.state.configLoaded) {
            return;
        }
        try {
            const cfg = await rpc("/tus_smart_global_search/config", {});
            this.state.allowedModels = Array.isArray(cfg.allowed_models)
                ? cfg.allowed_models
                : [];
        } catch {
            this.state.allowedModels = [];
        } finally {
            this.state.configLoaded = true;
        }
    }

    /** Models allowed for this user (none until config loads; empty list = none). */
    isModelAllowed(model) {
        if (!this.state.configLoaded || !this.state.allowedModels.length) {
            return false;
        }
        return this.state.allowedModels.includes(model);
    }

    get filteredSuggestions() {
        if (!this.state.configLoaded) {
            return [];
        }
        const allowed = this.state.allowedModels;
        return SEARCH_SUGGESTIONS.filter((sug) => suggestionMatchesAllowedModels(sug, allowed));
    }

    get filteredFavourites() {
        if (!this.state.configLoaded || !this.state.allowedModels.length) {
            return [];
        }
        const allowed = this.state.allowedModels;
        return this.state.favourites.filter((f) => allowed.includes(f.model));
    }

    get filteredFrequent() {
        if (!this.state.configLoaded || !this.state.allowedModels.length) {
            return [];
        }
        const allowed = this.state.allowedModels;
        return this.state.frequent.filter((f) => allowed.includes(f.model));
    }

    /** True when the user must pick Global Search Models before text/browse search works. */
    get showNoModelsConfigured() {
        if (!this.state.configLoaded || this.state.allowedModels.length > 0) {
            return false;
        }
        return (
            this.state.browseMode ||
            (this.state.query && this.state.query.trim().length >= 2)
        );
    }

    /** True when the results list should be shown (text search ≥2 chars, or browse chip). */
    get showResultsPanel() {
        return (
            this.state.browseMode ||
            (this.state.query && this.state.query.trim().length >= 2)
        );
    }

    get flatResultItems() {
        const items = [];
        for (const group of this.state.groups) {
            for (const result of group.results) {
                items.push({ group, result });
            }
        }
        return items;
    }

    getFlatIndex(groupIndex, resultIndex) {
        let idx = 0;
        for (let g = 0; g < this.state.groups.length; g++) {
            if (g < groupIndex) {
                idx += this.state.groups[g].results.length;
            } else {
                return idx + resultIndex;
            }
        }
        return idx;
    }

    getImageUrl(model, id) {
        return url("/web/image", {
            model,
            id,
            field: "image_1920",
        });
    }

    onInput() {
        this.state.browseMode = false;
        this.state.browseModel = null;
        this.state.browsePreset = null;
        this.state.query = this.inputRef.el?.value ?? this.state.query;
        this.state.selectedIndex = 0;
        this.state.error = false;
        if (this.state.query.length >= 2) {
            if (this.state.configLoaded && !this.state.allowedModels.length) {
                this.state.groups = [];
                this.state.loading = false;
                return;
            }
            this.state.loading = true;
            this._search();
        } else {
            this.state.groups = [];
            this.state.recentSearches = getRecentSearches();
            this.state.favourites = getFavourites();
            this.state.frequent = getFrequentRecords().slice(0, FREQUENT_SHOW);
        }
    }

    async doSearch() {
        const query = this.state.query.trim();
        if (query.length < 2) {
            this.state.loading = false;
            return;
        }
        await this.loadConfigIfNeeded(false);
        if (!this.state.allowedModels.length) {
            this.state.groups = [];
            this.state.loading = false;
            this.state.selectedIndex = 0;
            return;
        }
        // Bump request counter; capture local copy to detect stale responses.
        const reqId = ++this._reqId;
        try {
            const { groups } = await rpc("/tus_smart_global_search/search", { query });
            // Discard result if a newer request has already been issued.
            if (reqId !== this._reqId) return;
            this.state.groups = groups || [];
            this.state.selectedIndex = 0;
        } catch (e) {
            if (reqId !== this._reqId) return;
            this.state.groups = [];
            this.state.error = true;
        } finally {
            if (reqId === this._reqId) {
                this.state.loading = false;
            }
        }
    }

    setSelectedIndex(index) {
        const inResults =
            this.state.browseMode ||
            (this.state.query && this.state.query.length >= 2);
        const max = inResults
            ? this.flatResultItems.length - 1
            : Math.max(0, this.state.recentSearches.length - 1);
        this.state.selectedIndex = Math.max(0, Math.min(index, max));
    }

    selectRecent(term) {
        this.state.browseMode = false;
        this.state.browseModel = null;
        this.state.browsePreset = null;
        this.state.query = term;
        if (this.inputRef.el) this.inputRef.el.value = term;
        this.state.groups = [];
        this.state.error = false;
        if (this.state.configLoaded && !this.state.allowedModels.length) {
            this.state.loading = false;
            return;
        }
        this.state.loading = true;
        this._search();
    }

    removeRecent(term) {
        let recent = getRecentSearches().filter((t) => t !== term);
        try {
            localStorage.setItem(RECENT_STORAGE_KEY, JSON.stringify(recent));
        } catch {}
        this.state.recentSearches = recent;
    }

    clearSearchHistory() {
        clearRecentSearches();
        this.state.recentSearches = [];
        this.state.selectedIndex = 0;
    }

    async applySuggestion(suggestion) {
        if (suggestion.model) {
            await this.loadBrowse(suggestion);
            return;
        }
        this.state.browseMode = false;
        this.state.browseModel = null;
        this.state.browsePreset = null;
        const q = suggestion.query || suggestion.label || "";
        this.state.query = q;
        if (this.inputRef.el) this.inputRef.el.value = q;
        this.state.groups = [];
        this.state.error = false;
        if (q.length >= 2) {
            if (this.state.configLoaded && !this.state.allowedModels.length) {
                this.state.loading = false;
                return;
            }
            this.state.loading = true;
            this._search();
        }
    }

    async loadBrowse(suggestion) {
        const label = suggestion.label || "";
        this.state.browseMode = true;
        this.state.browseModel = suggestion.model || null;
        this.state.browsePreset = suggestion.browse_preset || null;
        this.state.error = false;
        this.state.groups = [];
        this.state.query = label;
        if (this.inputRef.el) {
            this.inputRef.el.value = label;
        }
        await this.loadConfigIfNeeded(false);
        if (!this.state.allowedModels.length) {
            this.state.loading = false;
            this.state.browseMode = false;
            this.state.browseModel = null;
            this.state.browsePreset = null;
            return;
        }
        this.state.loading = true;
        const reqId = ++this._reqId;
        try {
            const payload = {
                model: suggestion.model,
                limit: 80,
            };
            if (suggestion.browse_preset) {
                payload.browse_preset = suggestion.browse_preset;
            }
            const { groups } = await rpc("/tus_smart_global_search/browse", payload);
            if (reqId !== this._reqId) {
                return;
            }
            this.state.groups = groups || [];
            this.state.selectedIndex = 0;
        } catch (e) {
            if (reqId !== this._reqId) {
                return;
            }
            this.state.groups = [];
            this.state.error = true;
        } finally {
            if (reqId === this._reqId) {
                this.state.loading = false;
            }
        }
    }

    async openFullListFromBrowse() {
        if (!this.state.browseModel) {
            return;
        }
        try {
            const nav = await rpc("/tus_smart_global_search/browse_list_nav", {
                model: this.state.browseModel,
                browse_preset: this.state.browsePreset || null,
            });
            const actionId = nav && nav.action != null ? Number(nav.action) : NaN;
            if (!Number.isFinite(actionId)) {
                const fallback = await rpc("/tus_smart_global_search/browse_action", {
                    model: this.state.browseModel,
                    browse_preset: this.state.browsePreset || null,
                });
                if (fallback && fallback.type) {
                    await this.action.doAction(fallback);
                }
                queueMicrotask(() => this.props.close());
                return;
            }
            const url = `${window.location.origin}${router.stateToUrl({
                actionStack: [{ action: actionId }],
            })}`;
            const w = window.open(url, "_blank");
            if (!w) {
                const action = await rpc("/tus_smart_global_search/browse_action", {
                    model: this.state.browseModel,
                    browse_preset: this.state.browsePreset || null,
                });
                if (action && action.type) {
                    await this.action.doAction(action);
                }
            }
            queueMicrotask(() => this.props.close());
        } catch (e) {
            this.state.error = true;
        }
    }

    isFavourite(model, id) {
        return this.state.favourites.some((f) => f.model === model && f.id === id);
    }

    toggleFavourite(model, result, ev) {
        ev.stopPropagation();
        let favs = getFavourites();
        const exists = favs.findIndex((f) => f.model === model && f.id === result.id);
        if (exists >= 0) {
            favs = favs.filter((f) => !(f.model === model && f.id === result.id));
        } else {
            favs = [
                {
                    model,
                    id: result.id,
                    display_name: result.display_name || "",
                },
                ...favs,
            ].slice(0, FAVOURITES_MAX);
        }
        saveFavourites(favs);
        this.state.favourites = favs;
    }

    removeFavouriteEntry(model, id) {
        const favs = getFavourites().filter((f) => !(f.model === model && f.id === id));
        saveFavourites(favs);
        this.state.favourites = favs;
    }

    async openRecord(model, result) {
        addRecentSearch(this.state.query);
        this.state.frequent = recordFrequentAccess(model, result).slice(0, FREQUENT_SHOW);
        const rid = Number(result.id);
        try {
            let action = await rpc("/tus_smart_global_search/open_record_action", {
                model,
                res_id: rid,
            });
            if (!action || !action.type) {
                action = {
                    type: "ir.actions.act_window",
                    name: result.display_name || model,
                    res_model: model,
                    res_id: rid,
                    views: [[false, "form"]],
                    target: "current",
                };
            }
            if (action && action.type) {
                await this.action.doAction(action);
            }
        } catch (e) {
            await this.action.doAction({
                type: "ir.actions.act_window",
                name: result.display_name || model,
                res_model: model,
                res_id: rid,
                views: [[false, "form"]],
                target: "current",
            });
        } finally {
            queueMicrotask(() => this.props.close());
        }
    }

    async openFavouriteEntry(entry) {
        const result = { id: entry.id, display_name: entry.display_name || "" };
        await this.openRecord(entry.model, result);
    }

    async openRecordInNewTab(model, result, ev) {
        if (ev) ev.stopPropagation();
        addRecentSearch(this.state.query);
        this.state.frequent = recordFrequentAccess(model, result).slice(0, FREQUENT_SHOW);
        const url = urlToOpenRecordInNewTab(model, result.id);
        window.open(url, "_blank");
    }

    highlightSegments(displayName) {
        const q = this.state.browseMode ? "" : this.state.query;
        return getHighlightSegments(displayName, q);
    }

    onKeydown(ev) {
        const hasResults =
            this.state.browseMode ||
            (this.state.query && this.state.query.length >= 2);
        const flat = this.flatResultItems;
        const recent = this.state.recentSearches;
        const n = hasResults ? flat.length : recent.length;
        if (n === 0) return;

        if (ev.key === "ArrowDown") {
            ev.preventDefault();
            this.setSelectedIndex(this.state.selectedIndex + 1);
            return;
        }
        if (ev.key === "ArrowUp") {
            ev.preventDefault();
            this.setSelectedIndex(this.state.selectedIndex - 1);
            return;
        }
        if (ev.key === "Enter") {
            ev.preventDefault();
            if (
                !this.state.browseMode &&
                this.state.query.length < 2 &&
                this.state.recentSearches.length
            ) {
                const term = this.state.recentSearches[this.state.selectedIndex];
                if (term) this.selectRecent(term);
                return;
            }
            const item = this.flatResultItems[this.state.selectedIndex];
            if (item && item.group && item.result) {
                this.openRecord(item.group.model, item.result);
            }
        }
        if (ev.key === "Escape") {
            ev.preventDefault();
            this.props.close();
        }
    }
}

export class GlobalSearchSystray extends Component {
    static template = "tus_smart_global_search.GlobalSearchSystray";
    static components = { GlobalSearchPanel };
    static props = {};

    setup() {
        this.triggerRef = useRef("trigger");
        this.state = useState({ configured: false, modelCount: 0 });

        this.popover = usePopover(GlobalSearchPanel, {
            position: "bottom",
            popoverClass: "o_global_search_popover",
        });

        onMounted(() => this._loadConfig());
        onWillUnmount(() => this.popover.close());
    }

    async _loadConfig() {
        try {
            const result = await rpc("/tus_smart_global_search/config", {});
            this.state.configured = result.configured || false;
            this.state.modelCount = result.model_count || 0;
        } catch {
            // Not an admin or network error — hide the indicator silently.
        }
    }

    openSearch() {
        if (this.popover.isOpen) {
            this.popover.close();
            return;
        }
        const target = this.triggerRef.el;
        if (!target) return;
        this.popover.open(target, {
            close: () => this.popover.close(),
        });
    }
}

export const systrayItem = {
    Component: GlobalSearchSystray,
};
registry.category("systray").add("tus_smart_global_search", systrayItem, { sequence: 2 });