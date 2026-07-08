/** @odoo-module **/

import { registry } from "@web/core/registry";
import { user, userBus } from "@web/core/user";

const CACHE_TTL_MS = 5 * 60 * 1000;

export const ringcentralAccessService = {
    async start() {
        let cache = null;
        let cacheAt = 0;

        const currentCompanyId = () => user.activeCompany?.id || false;

        const fetchSession = async () => {
            const now = Date.now();
            if (cache && now - cacheAt < CACHE_TTL_MS) {
                return cache;
            }
            try {
                const response = await fetch("/ringcentral/api/session", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    credentials: "include",
                    body: JSON.stringify({
                        jsonrpc: "2.0",
                        method: "call",
                        params: {},
                        id: Math.floor(Math.random() * 1000000),
                    }),
                });
                const payload = response.ok ? await response.json() : {};
                const result = payload.result || payload;
                cache = result?.data || {
                    has_access: false,
                    is_admin: false,
                    is_connected: false,
                    has_config: false,
                    company_id: currentCompanyId(),
                };
            } catch {
                cache = {
                    has_access: false,
                    is_admin: false,
                    is_connected: false,
                    has_config: false,
                    company_id: currentCompanyId(),
                };
            }
            cacheAt = now;
            return cache;
        };

        userBus.addEventListener("ACTIVE_COMPANIES_CHANGED", () => {
            cache = null;
            cacheAt = 0;
        });

        await fetchSession();

        return {
            get hasAccess() {
                return Boolean(cache?.has_access);
            },
            get isAdmin() {
                return Boolean(cache?.is_admin);
            },
            get isConnected() {
                return Boolean(cache?.is_connected);
            },
            get hasConfig() {
                return Boolean(cache?.has_config);
            },
            get canLoadWidget() {
                return Boolean(cache?.has_access);
            },
            get needsAdminConfig() {
                return Boolean(cache?.has_access && !cache?.has_config);
            },
            async refresh() {
                return fetchSession();
            },
            async getSession() {
                return fetchSession();
            },
        };
    },
};

registry.category("services").add("ringcentral.access", ringcentralAccessService);
