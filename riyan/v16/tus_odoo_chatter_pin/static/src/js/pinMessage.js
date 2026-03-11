/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Message } from "@mail/components/message/message";

async function rpcCall(method, model, args, kwargs) {
    const response = await fetch("/web/dataset/call_kw", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            jsonrpc: "2.0",
            id: Math.floor(Math.random() * 10000),
            method: "call",
            params: { model: model || "mail.message", method, args: args || [], kwargs: kwargs || {} },
        }),
    });
    const data = await response.json();
    if (data.error) throw new Error(JSON.stringify(data.error));
    return data.result;
}

function getThreadInfo() {
    const chatterEl = document.querySelector(".o_Chatter");
    if (chatterEl) {
        let node = chatterEl.__owl__;
        while (node) {
            const comp = node.component;
            if (comp) {
                if (comp.thread && comp.thread.id && comp.thread.model)
                    return { resId: comp.thread.id, resModel: comp.thread.model };
                const p = comp.props || {};
                const resId = p.resId || p.res_id || p.threadId || p.thread_id;
                const resModel = p.resModel || p.res_model || p.threadModel || p.thread_model;
                if (resId && resModel) return { resId, resModel };
            }
            node = node.parent;
        }
    }
    const hash = window.location.hash.replace("#", "");
    const params = {};
    hash.split("&").forEach(part => {
        const [k, v] = part.split("=");
        if (k && v) params[decodeURIComponent(k)] = decodeURIComponent(v);
    });
    if (params.id && params.model) return { resId: parseInt(params.id), resModel: params.model };
    return null;
}

function waitForChatter(callback, maxWait = 10000) {
    const start = Date.now();
    const check = () => {
        if (document.querySelector(".o_Chatter")) {
            callback();
        } else if (Date.now() - start < maxWait) {
            setTimeout(check, 300);
        }
    };
    check();
}

function formatDate(dateStr) {
    if (!dateStr) return "";
    try {
        const d = new Date(dateStr.replace(" ", "T") + "Z");
        return d.toLocaleDateString(undefined, { month: "short", day: "numeric" })
             + " " + d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
    } catch { return dateStr; }
}

function getInitials(name) {
    if (!name) return "?";
    return name.split(" ").map(w => w[0]).join("").substring(0, 2).toUpperCase();
}

function renderPinnedPanel(messages) {
    const chatterEl = document.querySelector(".o_Chatter");
    if (!chatterEl) return;

    const existing = chatterEl.querySelector(".o_tus_PinnedPanel");
    if (existing) existing.remove();
    if (!messages || !messages.length) return;

    const panel = document.createElement("div");
    panel.className = "o_tus_PinnedPanel";

    const header = document.createElement("div");
    header.className = "o_tus_header";
    header.innerHTML = `
        <i class="fa fa-fw fa-caret-down o_tus_caret"></i>
        <span>Pinned Messages</span>
        <span class="badge rounded-pill text-bg-primary ms-1 o_tus_badge">${messages.length}</span>
    `;
    panel.appendChild(header);

    const body = document.createElement("div");
    body.className = "o_tus_body";

    messages.forEach((msg) => {
        const initials = getInitials(msg.author_name);
        const avatarHtml = msg.author_id
            ? `<img class="o_tus_avatar" src="/web/image/res.partner/${msg.author_id}/avatar_128" alt="${msg.author_name}"/>`
            : `<div class="o_tus_avatar_placeholder">${initials}</div>`;

        const bodyText = (msg.body || "").replace(/<[^>]*>/g, "").trim();

        const item = document.createElement("div");
        item.className = "o_PinnedMessage_item";
        item.innerHTML = `
            <div class="o_tus_author_row">
                ${avatarHtml}
                <span class="o_tus_author_name">${msg.author_name || "Unknown"}</span>
                <i class="fa fa-envelope o_tus_email_icon"></i>
                <span class="o_tus_pin_date">${formatDate(msg.pinned_at)}</span>
            </div>
            <div class="o_tus_msg_body">${bodyText}</div>
            <div class="o_tus_actions">
                <button class="btn btn-sm btn-light o_tus_jump" data-id="${msg.id}">Jump</button>
                <button class="btn btn-sm btn-warning o_tus_unpin" data-id="${msg.id}">
                    <i class="fa fa-thumb-tack me-1"></i>Unpin
                </button>
            </div>
        `;
        body.appendChild(item);
    });

    panel.appendChild(body);

    let isOpen = true;
    header.addEventListener("click", () => {
        isOpen = !isOpen;
        body.style.display = isOpen ? "block" : "none";
        panel.querySelector(".o_tus_caret").className =
            `fa fa-fw o_tus_caret ${isOpen ? "fa-caret-down" : "fa-caret-right"}`;
        panel.querySelector(".o_tus_badge").style.display = isOpen ? "none" : "";
    });

    body.querySelectorAll(".o_tus_jump").forEach(btn => {
        btn.addEventListener("click", (ev) => {
            ev.stopPropagation();
            const id = btn.dataset.id;
            const el = document.querySelector(
                `.o_Message[data-message-id="${id}"], .o_Message[data-id="${id}"]`
            );
            if (el) {
                el.scrollIntoView({ behavior: "smooth", block: "center" });
                el.classList.add("o_pinned_message_highlight");
                setTimeout(() => el.classList.remove("o_pinned_message_highlight"), 2200);
            }
        });
    });

    body.querySelectorAll(".o_tus_unpin").forEach(btn => {
        btn.addEventListener("click", async (ev) => {
            ev.stopPropagation();
            await rpcCall("toggle_pin_chatter", "mail.message", [[parseInt(btn.dataset.id)]]);
            const msgEl = document.querySelector(
                `.o_Message[data-message-id="${btn.dataset.id}"], .o_Message[data-id="${btn.dataset.id}"]`
            );
            if (msgEl) {
                const pinBtn = msgEl.querySelector(".o_tus_pin_btn");
                if (pinBtn) { pinBtn.title = "Pin"; pinBtn.style.color = ""; }
            }
            await reloadPinnedPanel();
        });
    });

    const topbar = chatterEl.querySelector(".o_ChatterTopbar");
    if (topbar) topbar.insertAdjacentElement("afterend", panel);
    else chatterEl.insertAdjacentElement("afterbegin", panel);
}

async function reloadPinnedPanel() {
    const info = getThreadInfo();
    if (!info) return;
    try {
        const messages = await rpcCall("get_pinned_messages_data", "mail.message", [info.resId, info.resModel], {});
        renderPinnedPanel(messages || []);
    } catch (e) {
        console.error("[TUS Pin] reloadPinnedPanel error:", e);
    }
}

function injectPinButton(msgEl) {
    if (msgEl.querySelector(".o_tus_pin_btn")) return;
    const msgId = parseInt(msgEl.dataset.messageId || msgEl.dataset.id);
    if (!msgId) return;

    const btn = document.createElement("button");
    btn.className = "o_tus_pin_btn";
    btn.type = "button";
    btn.title = "Pin";
    btn.innerHTML = '<i class="fa fa-thumb-tack"></i>';

    btn.addEventListener("click", async (ev) => {
        ev.stopPropagation();
        ev.preventDefault();
        try {
            const isPinned = await rpcCall("toggle_pin_chatter", "mail.message", [[msgId]]);
            btn.title = isPinned ? "Unpin" : "Pin";
            btn.style.color = isPinned ? "#d97706" : "";
            btn.classList.toggle("tus_pinned", isPinned);
            await reloadPinnedPanel();
        } catch (e) {
            console.error("[TUS Pin] toggle failed:", e);
        }
    });

    let actionsEl = msgEl.querySelector(".o_Message_actions");
    if (actionsEl) {
        actionsEl.prepend(btn);
    } else {
        btn.style.cssText = "position:absolute;top:6px;right:6px;z-index:2;";
        msgEl.style.position = "relative";
        msgEl.appendChild(btn);
    }
}

function init() {
    new MutationObserver((mutations) => {
        let chatterAppeared = false;
        for (const mutation of mutations) {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType !== 1) return;
                if (node.classList && node.classList.contains("o_Message")) injectPinButton(node);
                if (node.querySelectorAll) node.querySelectorAll(".o_Message").forEach(injectPinButton);
                if (
                    (node.classList && node.classList.contains("o_Chatter")) ||
                    (node.querySelectorAll && node.querySelector && node.querySelector(".o_Chatter"))
                ) chatterAppeared = true;
            });
        }
        if (chatterAppeared) setTimeout(reloadPinnedPanel, 500);
    }).observe(document.body, { childList: true, subtree: true });

    waitForChatter(() => {
        document.querySelectorAll(".o_Message").forEach(injectPinButton);
        reloadPinnedPanel();
    });
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
else init();

patch(Message.prototype, "tus_odoo_chatter_pin.Message", {
    setup() { this._super(...arguments); },
});