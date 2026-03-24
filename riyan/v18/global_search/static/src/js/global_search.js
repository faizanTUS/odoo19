/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { debounce } from "@web/core/utils/timing";
import { imageUrl } from "@web/core/utils/urls";

import { Component, useState, useRef, onWillUnmount, onMounted } from "@odoo/owl";
import { usePopover } from "@web/core/popover/popover_hook";

const RECENT_STORAGE_KEY = "global_search_recent";
const RECENT_MAX = 10;
const SEARCH_DEBOUNCE_MS = 300;

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

export class GlobalSearchPanel extends Component {
    static template = "global_search.GlobalSearchPanel";
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
            loading: false,
            error: false,
            groups: [],
            recentSearches: getRecentSearches(),
            selectedIndex: 0,
        });

        // Stale-request guard: only the latest request's results are applied.
        this._reqId = 0;

        this._search = debounce(this.doSearch.bind(this), SEARCH_DEBOUNCE_MS);

        // Auto-focus input when panel mounts.
        onMounted(() => setTimeout(() => this.inputRef.el?.focus(), 0));
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
        return imageUrl(model, id, "image_1920", {});
    }

    onInput() {
        this.state.query = this.inputRef.el?.value ?? this.state.query;
        this.state.selectedIndex = 0;
        this.state.error = false;
        if (this.state.query.length >= 2) {
            this.state.loading = true;
            this._search();
        } else {
            this.state.groups = [];
            this.state.recentSearches = getRecentSearches();
        }
    }

    async doSearch() {
        const query = this.state.query.trim();
        if (query.length < 2) {
            this.state.loading = false;
            return;
        }
        // Bump request counter; capture local copy to detect stale responses.
        const reqId = ++this._reqId;
        try {
            const { groups } = await rpc("/global_search/search", { query });
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
        const max = this.state.query && this.state.query.length >= 2
            ? this.flatResultItems.length - 1
            : Math.max(0, this.state.recentSearches.length - 1);
        this.state.selectedIndex = Math.max(0, Math.min(index, max));
    }

    selectRecent(term) {
        this.state.query = term;
        if (this.inputRef.el) this.inputRef.el.value = term;
        this.state.groups = [];
        this.state.error = false;
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

    async openRecord(model, result) {
        addRecentSearch(this.state.query);
        try {
            const action = await this.orm.call(model, "get_formview_action", [[result.id]], {});
            await this.action.doAction(action);
        } catch (e) {
            await this.action.doAction({
                type: "ir.actions.act_window",
                name: result.display_name || model,
                res_model: model,
                res_id: result.id,
                views: [[false, "form"]],
                target: "current",
            });
        } finally {
            this.props.close();
        }
    }

    onKeydown(ev) {
        const hasResults = this.state.query && this.state.query.length >= 2;
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
            if (this.state.query.length < 2 && this.state.recentSearches.length) {
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
    static template = "global_search.GlobalSearchSystray";
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
            const result = await rpc("/global_search/config", {});
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
registry.category("systray").add("global_search", systrayItem, { sequence: 2 });