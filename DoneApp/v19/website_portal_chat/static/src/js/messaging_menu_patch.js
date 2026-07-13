/* @odoo-module */

import { MessagingMenu } from "@mail/core/public_web/messaging_menu";
import { onExternalClick } from "@mail/utils/common/hooks";
import { useEffect, useState, onWillStart, App } from "@odoo/owl";

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { MessagingMenuQuickSearch } from "@mail/core/web/messaging_menu_quick_search";
import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { getTemplate } from "@web/core/templates";
import { DiscussSearch } from "@mail/core/public_web/discuss_search";
import { ChatHub } from "@mail/core/common/chat_hub";

// Register components for use in templates
Object.assign(MessagingMenu.components, { MessagingMenuQuickSearch, ChatHub });

/**
 * SHARED HELPER: Open the "New Message" partner search modal.
 * This can be triggered from MessagingMenu button or DiscussSearch click on mobile.
 */
function openNewMessageModal(component) {
    const existing = document.getElementById("o_portal_chat_new_message_modal");
    if (existing) {
        existing.querySelector("input")?.focus();
        return;
    }

    const modal = document.createElement("div");
    modal.id = "o_portal_chat_new_message_modal";
    modal.className = "o_portal_chat_new_message_modal";

    const isMobile = component.ui.isSmall;
    const panelWidth = isMobile ? "100%" : "350px";
    const panelHeight = isMobile ? "100%" : "Min(95vh, 633.33px)";
    const panelBottom = isMobile ? "0" : "0.5rem";
    const panelRight = isMobile ? "0" : "1rem";
    const panelRadius = isMobile ? "0" : "8px 8px 0 0";

    modal.innerHTML = `
        <div class="o_portal_chat_new_message_backdrop" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 10000;"></div>
        <div class="o_portal_chat_new_message_panel card shadow" style="position: fixed; bottom: ${panelBottom}; right: ${panelRight}; width: ${panelWidth}; height: ${panelHeight}; max-width: 100vw; max-height: 100vh; background: #fff; border-radius: ${panelRadius}; box-shadow: 0 0 20px rgba(0, 0, 0, 0.15); z-index: 10001; display: flex; flex-direction: column; overflow: hidden;">
            <div class="card-header d-flex justify-content-between align-items-center" style="background-color: #875A7B !important; color: white; padding: 0.75rem 1rem; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
                <div class="fw-bold">${_t("New message")}</div>
                <button type="button" class="btn-close" aria-label="${_t("Close")}" style="filter: invert(1) grayscale(100%) brightness(200%);"></button>
            </div>
            <div class="card-body" style="flex: 1; display: flex; flex-direction: column; padding: 1rem; overflow-y: auto;">
                <div class="mb-3">
                    <label class="form-label small text-muted">${_t("Search a partner...")}</label>
                    <input type="text" class="form-control" placeholder="${_t("Name...")}"/>
                </div>
                <div class="o_portal_chat_new_message_results list-group overflow-auto" style="flex: 1;"></div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    const close = () => {
        modal.remove();
        if (component.dropdown?.close) component.dropdown.close();
    };
    modal.querySelector(".btn-close")?.addEventListener("click", close);
    modal.querySelector(".o_portal_chat_new_message_backdrop")?.addEventListener("click", close);

    const input = modal.querySelector("input");
    const resultsEl = modal.querySelector(".o_portal_chat_new_message_results");

    let lastReq = 0;
    const renderResults = (partners) => {
        resultsEl.innerHTML = "";
        if (!partners || partners.length === 0) {
            resultsEl.innerHTML = `<div class="p-3 text-center text-muted small">${_t("No partners found.")}</div>`;
            return;
        }
        for (const p of partners) {
            const item = document.createElement("button");
            item.className = "list-group-item list-group-item-action border-0 d-flex align-items-center gap-3 py-3";
            item.innerHTML = `
                <img class="rounded-circle" style="width: 40px; height: 40px; object-fit: cover;" src="${p.avatar_url || ""}" alt="" />
                <div class="flex-grow-1 text-start">
                    <div class="fw-bold">${p.name || ""}</div>
                    <div class="small text-muted">${p.im_status || ""}</div>
                </div>
            `;
            item.addEventListener("click", async () => {
                close();
                await openChatWithPartner(component, p.id);
            });
            resultsEl.appendChild(item);
        }
    };

    const doSearch = async (term) => {
        const reqId = ++lastReq;
        if (!term?.trim()) {
            resultsEl.innerHTML = "";
            return;
        }
        resultsEl.innerHTML = `<div class="p-3 text-center text-muted"><i class="fa fa-spinner fa-spin me-2"/>${_t("Searching...")}</div>`;
        try {
            const partners = await rpc("/website_portal_chat/search_partners", { term });
            if (reqId === lastReq) renderResults(partners || []);
        } catch (e) {
            resultsEl.innerHTML = `<div class="p-3 text-center text-danger small">${_t("Error searching partners.")}</div>`;
        }
    };

    let debounce;
    input.addEventListener("input", (e) => {
        clearTimeout(debounce);
        debounce = setTimeout(() => doSearch(e.target.value), 300);
    });
    setTimeout(() => input.focus(), 100);
}

/**
 * SHARED HELPER: Initiate chat with a partner and ensure it opens in the chat hub/window.
 */
async function openChatWithPartner(component, partnerId) {
    const store = component.store || component.env.services?.["mail.store"];
    await store.isReady;

    const data = await rpc("/website_portal_chat/get_thread_with_partner", { partner_id: partnerId });
    if (!data) return;

    store.insert(data);
    let thread;
    if (data["discuss.channel"]?.[0]) {
        const id = data["discuss.channel"][0].id;
        thread = store.Thread ? store.Thread.get(id) : store.models?.["discuss.channel"]?.get(id);
        if (!thread && store.Thread?.records) {
            thread = Object.values(store.Thread.records).find(t => t.id === id);
        }
    }

    if (thread) {
        // Force the thread to open in a chat window (Chat Hub)
        store.insert({ ChatWindow: [{ thread }] });
        const chatWindow = Object.values(store.ChatWindow?.records || {}).find(cw => cw.thread?.id === thread.id);
        chatWindow?.open();
        if (!component.ui.isSmall && !component.env.inDiscussApp) {
            component.dropdown?.close();
        }
    }
}

// Patch MessagingMenuQuickSearch to handle partner selection and open chat window correctly.
patch(MessagingMenuQuickSearch.prototype, {
    async onSelect(option) {
        if (option.partner) {
            await openChatWithPartner(this, option.partner.id);
            return;
        }
        return super.onSelect(option);
    },
});

// Patch DiscussSearch to intercept search clicks on mobile and open our custom modal.
patch(DiscussSearch.prototype, {
    onClickSearchConversations() {
        console.log("Portal Chat: DiscussSearch intercepted search click for mobile");
        if (this.ui.isSmall) {
            openNewMessageModal(this);
            return;
        }
        return super.onClickSearchConversations();
    },
});

patch(MessagingMenu.prototype, {
    async setup() {
        super.setup();
        this.pwa = useService("pwa");
        this.notification = useService("mail.notification.permission");
//        onWillStart(async () => {
//            const data = await rpc("/website_portal_chat/init", {});
//            this.store.insert(data.storeData);
//        });
        onWillStart(async () => {
            const data = await rpc("/website_portal_chat/init", {});
            this.store.insert(data.storeData);
            await this.store.isReady;
            this._setupNewChannelListener();
        });

        Object.assign(this.state, { searchOpen: false });
        // Store reference to this MessagingMenu instance for quick search component if needed
        if (this.store?.messaging) {
            this.store.messaging.menu = this;
        }
    },

    _setupNewChannelListener() {
        const busService = this.env.services?.bus_service;
        if (!busService) return;

        busService.addEventListener('notification', ({ detail: notifications }) => {
            for (const { payload, type } of notifications) {
                if (type === 'mail.record/insert' && payload?.['discuss.channel']) {
                    this.store.insert(payload);
                }
                if (type === 'discuss.channel/joined') {
                    const channelId = payload?.channel?.id;
                    if (channelId) {
                        busService.addChannel(`discuss.channel_${channelId}`);
                    }
                }
            }
        });
    },

    async openThread(thread) {
        thread.open({ focus: true, fromMessagingMenu: true });
        this.dropdown.close();
    },

    get visibleStandaloneMessages() {
        return this.store?.inbox ? super.visibleStandaloneMessages : [];
    },
    get visiblePreviews() {
        return this.store?.discuss ? super.visiblePreviews : [];
    },
    get threads() {
        return this.store ? super.threads : [];
    },
    beforeOpen() {
        if (!this.store) return;
        this.state.searchOpen = false;
        if (this.store.discuss) this.store.discuss.searchTerm = "";
        if (this.store.isReady && this.store.inbox) {
            this.store.isReady.then(() => {
                const inbox = this.store.inbox;
                if (inbox && !inbox.isLoaded && inbox.status !== "loading" && (inbox.counter || 0) !== (inbox.messages || []).length) {
                    inbox.fetchNewMessages();
                }
            });
        }
    },

    onClickSearchConversations() {
        if (this.ui.isSmall) {
            openNewMessageModal(this);
            return;
        }
        if (this.command) {
            this.command.openMainPalette({ searchValue: "@" });
            if (!this.ui.isSmall && !this.env.inDiscussApp) {
                this.dropdown?.close();
            }
        }
    },

    get canPromptToInstall() {
        return this.pwa?.canPromptToInstall;
    },
    get hasPreviews() {
        if (!this.store) return false;
        const activeTab = this.store.discuss?.activeTab || "main";
        return (
            (this.threads || []).length > 0 ||
            ((this.store.failures || []).length > 0 && activeTab === "main" && !this.env.inDiscussApp) ||
            (this.shouldAskPushPermission && activeTab === "main" && !this.env.inDiscussApp) ||
            (this.canPromptToInstall && activeTab === "main" && !this.env.inDiscussApp)
        );
    },
    get installationRequest() {
        return {
            body: _t("Come here often? Install Odoo on your device!"),
            displayName: _t("%s has a suggestion", this.store.odoobot?.name || _t("OdooBot")),
            onClick: () => this.pwa?.show(),
            iconSrc: this.store.odoobot?.avatarUrl,
            partner: this.store.odoobot,
            isShown: this.store.discuss?.activeTab === "main" && !this.env.inDiscussApp,
        };
    },
    get notificationRequest() {
        return {
            body: _t("Enable desktop notifications to chat"),
            displayName: _t("%s has a request", this.store.odoobot?.name || _t("OdooBot")),
            iconSrc: this.store.odoobot?.avatarUrl,
            partner: this.store.odoobot,
            onClick: () => this.notification?.requestPermission(),
            isShown: this.store.discuss?.activeTab === "main" && !this.env.inDiscussApp,
        };
    },
    get tabs() {
        return [
            {
                icon: this.env.inDiscussApp ? "fa fa-inbox" : "fa fa-envelope",
                id: "main",
                label: this.env.inDiscussApp ? _t("Mailboxes") : _t("All"),
            },
            ...super.tabs,
        ];
    },
    onClickFailure(failure) {
        const threadIds = new Set(failure.notifications.map(({ message }) => message.thread.id));
        if (threadIds.size === 1) {
            this.openThread(failure.notifications[0].message.thread);
        } else {
            this.openFailureView(failure);
            this.dropdown.close();
        }
    },
    onClickThread(isMarkAsRead, thread, message) {
        if (isMarkAsRead) {
            this.markAsRead(thread);
            return;
        }
        if (message?.needaction && message.message_type === "user_notification") {
            this.store.inbox.highlightMessage = message;
            this.store.inbox.open();
            return;
        }
        this.openThread(thread);
    },
    openFailureView(failure) {
        if (failure.type !== "email") return;
        this.action.doAction({
            name: _t("Mail Failures"),
            type: "ir.actions.act_window",
            view_mode: "kanban,list,form",
            views: [[false, "kanban"], [false, "list"], [false, "form"]],
            target: "current",
            res_model: failure.resModel,
            domain: [["message_has_error", "=", true]],
            context: { create: false },
        });
    },
    cancelNotifications(failure) {
        return this.env.services.orm.call(failure.resModel, "notify_cancel_by_type", [], {
            notification_type: failure.type,
        });
    },

    get counter() {
        if (!this.store) return 0;
        const inboxCounter = this.store.inbox?.counter || 0;
        const failuresCounter = (this.store.failures || []).reduce((acc, f) => acc + parseInt(f.notifications.length), 0);
        return inboxCounter + failuresCounter;
    },
    get displayStartConversation() {
        return (this.store?.discuss?.activeTab || "main") !== "channel";
    },
    get shouldAskPushPermission() {
        return this.notification?.permission === "prompt";
    },
    getFailureNotificationName(failure) {
        return failure.type === "email"
            ? _t("Email Failure: %(modelName)s", { modelName: failure.modelName })
            : _t("Failure: %(modelName)s", { modelName: failure.modelName });
    },

    onClickNewMessage() {
        //        openNewMessageModal(this);
        this._openNewMessageModal();
    },

    _openNewMessageModal() {
        const existing = document.getElementById("o_portal_chat_new_message_modal");
        if (existing) {
            existing.querySelector("input")?.focus();
            return;
        }

        const modal = document.createElement("div");
        modal.id = "o_portal_chat_new_message_modal";
        modal.className = "o_portal_chat_new_message_modal";

        // Use inline styles for maximum reliability on portal/mobile transitions
        const isMobile = this.ui.isSmall;
        const panelWidth = isMobile ? "100%" : "350px";
        const panelHeight = isMobile ? "100%" : "Min(95vh, 633.33px)";
        const panelBottom = isMobile ? "0" : "0.5rem";
        const panelRight = isMobile ? "0" : "1rem";
        const panelRadius = isMobile ? "0" : "8px 8px 0 0";

        modal.innerHTML = `
         <div class="o_portal_chat_new_message_backdrop" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 10000;"></div>
         <div class="o_portal_chat_new_message_panel card shadow" style="position: fixed;
            bottom: ${panelBottom};
            right: ${panelRight};
            width: ${panelWidth};
            height: ${panelHeight};
            max-width: 100vw;
            max-height: 100vh;
            background: #fff;
            border-radius: ${panelRadius};
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
            z-index: 10001;
            display: flex;
            flex-direction: column;
            overflow: hidden;">
             <div class="card-header d-flex justify-content-between align-items-center" style="background-color: #875A7B !important;
            color: white;
            padding: 0.75rem 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
                 <div class="fw-bold">${_t("New message")}</div>
                 <button type="button" class="btn-close" aria-label="${_t("Close")}" style="filter: invert(1) grayscale(100%) brightness(200%);"></button>
             </div>
             <div class="card-body" style="flex: 1;
            display: flex;
            flex-direction: column;
            padding: 1rem;
            overflow-y: auto;">
                 <div class="mb-3">
                     <label class="form-label small text-muted">${_t("Search a partner...")}</label>
                     <input type="text" class="form-control" placeholder="${_t("Name...")}" autofocus="1"/>
                 </div>
                 <div class="o_portal_chat_new_message_results list-group overflow-auto" style="flex: 1;"></div>
             </div>
         </div>
     `  ;
        document.body.appendChild(modal);

        const close = () => {
            modal.remove();
            // Try to close dropdown if any
            this.dropdown?.close();
        };
        modal.querySelector(".btn-close")?.addEventListener("click", close);
        modal.querySelector(".o_portal_chat_new_message_backdrop")?.addEventListener("click", close);

        const input = modal.querySelector("input");
        const resultsEl = modal.querySelector(".o_portal_chat_new_message_results");

        let lastReq = 0;
        const renderResults = (partners) => {
            resultsEl.innerHTML = "";
            if (!partners || partners.length === 0) {
                resultsEl.innerHTML = `<div class="p-3 text-center text-muted small">${_t("No partners found.")}</div>`;
                return;
            }
            for (const p of partners) {
                const item = document.createElement("button");
                item.type = "button";
                item.className = "list-group-item list-group-item-action border-0 d-flex align-items-center gap-3 py-3";
                item.innerHTML = `
                 <img class="rounded-circle" style="width: 40px; height: 40px; object-fit: cover;" src="${p.avatar_url || ""}" alt="" />
                 <div class="flex-grow-1 text-start">
                     <div class="fw-bold">${p.name || ""}</div>
                     <div class="small text-muted">${p.im_status || ""}</div>
                 </div>
             `;
                item.addEventListener("click", async () => {
                    try {
                        close();
                        await this.openChatWithPartner(p.id);
                    } catch (e) {
                        console.error("Failed to open chat with partner", e);
                    }
                });
                resultsEl.appendChild(item);
            }
        };

        const doSearch = async (term) => {
            const reqId = ++lastReq;
            if (!term || term.trim().length < 1) {
                resultsEl.innerHTML = "";
                return;
            }
            resultsEl.innerHTML = `<div class="p-3 text-center text-muted"><i class="fa fa-spinner fa-spin me-2"/>${_t("Searching...")}</div>`;
            try {
                const partners = await rpc("/website_portal_chat/search_partners", { term });
                if (reqId !== lastReq) return;
                renderResults(Array.isArray(partners) ? partners : []);
            } catch (e) {
                console.error("Search RPC failed", e);
                resultsEl.innerHTML = `<div class="p-3 text-center text-danger small">${_t("Error searching partners.")}</div>`;
            }
        };

        let debounce;
        input.addEventListener("input", (e) => {
            clearTimeout(debounce);
            debounce = setTimeout(() => doSearch(e.target.value.trim()), 300);
        });

        // Forced focus
        setTimeout(() => input.focus(), 100);
    },

    async openChatWithPartner(partnerId) {
        await openChatWithPartner(this, partnerId);
    },

    async onClickMessagingMenu() {
        if (this.ui.isSmall) {
            openNewMessageModal(this);
            return;
        }
        this.dropdown?.toggle();
    },
});
