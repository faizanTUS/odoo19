/** @odoo-module **/

import {registry} from "@web/core/registry";
import {Component, onWillStart, useState, useRef, onMounted} from "@odoo/owl";
import { Layout } from "@web/search/layout";
import {useService} from "@web/core/utils/hooks";
import { renderToElement } from "@web/core/utils/render";
import {cookie} from "@web/core/browser/cookie";
import {browser} from "@web/core/browser/browser";
const {DateTime} = luxon;
import {user} from "@web/core/user";

export class ChatBot extends Component {
    setup() {
        this.messagesDiv = useRef("messages");
        this.messageInput = useRef("messageInput");
        this.orm = useService("orm");
        this.user = user;
        this.state = useState({
            isloading: false,
            history: [],
            todayHistory: [],
            yesterdayHistory: [],
            olderHistory: [],
            chatbot_session_id: null,
        });

        onWillStart(async () => {
            this.state.history = await this.loadHistory();
            const sessionID = cookie.get("chatbot_session_id");
            if (sessionID) {
                this.state.chatbot_session_id = parseInt(sessionID);
            }
        });

        onMounted(async () => {
            if (this.state.chatbot_session_id) {
                await this.loadSpecificHistory(this.state.chatbot_session_id);
            }
        });
    }

    async startNewChat() {
        this.state.chatbot_session_id = null;
        this.messagesDiv.el.innerHTML = "";
    }

    async loadHistory() {
        const history = await this.orm.searchRead(
            "chatbot.session",
            [["partner_id", "=", this.user.partnerId]],
            ["name", "create_date"],
            {order: "id desc"}
        );

        const today = DateTime.local().startOf("day");
        const yesterday = DateTime.local().minus({days: 1}).startOf("day");

        this.state.todayHistory = history.filter((session) =>
            DateTime.fromFormat(session.create_date, "yyyy-MM-dd HH:mm:ss").hasSame(
                today,
                "day"
            )
        );

        this.state.yesterdayHistory = history.filter((session) =>
            DateTime.fromFormat(session.create_date, "yyyy-MM-dd HH:mm:ss").hasSame(
                yesterday,
                "day"
            )
        );

        this.state.olderHistory = history.filter((session) => {
            const sessionDate = DateTime.fromFormat(
                session.create_date,
                "yyyy-MM-dd HH:mm:ss"
            );
            return (
                !sessionDate.hasSame(today, "day") &&
                !sessionDate.hasSame(yesterday, "day")
            );
        });

        return history;
    }

    async refreshHistory() {
        await this.loadHistory();
    }

    async loadSpecificHistory(history_id) {
        this.state.chatbot_session_id = history_id;
        cookie.set('chatbot_session_id', this.state.chatbot_session_id);
        const history = await this.orm.searchRead("chat.history", [['chatbot_session_id', '=', history_id]], ['user_input', 'bot_response_json']);

        this.messagesDiv.el.innerHTML = '';

        const formatDate = date => DateTime.fromISO(date).toFormat('yyyy-MM-dd');

        history.forEach(record => {
            this.messagesDiv.el.insertAdjacentHTML('beforeend', `
                <div class="user-message">
                    <h4>${this.user.name}</h4>
                    <div class="o-mail-Message-content o-min-width-0">${record.user_input}</div>
                </div>
            `);
            this.messagesDiv.el.insertAdjacentHTML('beforeend', '<h3>AI Bot</h3>');

            // Use the renderResponse method
            this.renderResponse(record.bot_response_json, formatDate);
        });

        if (this.messagesDiv.el.lastElementChild) {
            this.messagesDiv.el.lastElementChild.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
    }


    renderResponse(response, formatDate) {
    const createTable = (data) => {
        const rows = Array.isArray(data) ? data : [data];
        if (rows.length === 0) return '<p>No data available</p>';

        // Collect all unique keys from all objects
        const allKeys = new Set();
        rows.forEach(row => {
            if (row && typeof row === 'object') {
                Object.keys(row).forEach(key => allKeys.add(key));
            }
        });
        const keys = Array.from(allKeys);

        if (keys.length === 0) return '<p>No data available</p>';

        return `
            <table border="1" class="table" style="border-collapse: collapse; width: 100%;">
                <thead style="background-color: #f2f2f2;">
                    <tr>${keys.map(k => `<th style="padding: 8px; border: 1px solid #ddd;">${k.toUpperCase().replace(/_/g, ' ')}</th>`).join('')}</tr>
                </thead>
                <tbody>
                    ${rows.map(row => `
                        <tr style="text-align: left;">
                            ${keys.map(key => {
                                let value = row[key];

                                // Format dates
                                if (['create_date', 'date_order', 'write_date'].includes(key) && value) {
                                    value = formatDate(value);
                                }
                                // Handle nested objects (like address)
                                else if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
                                    value = Object.entries(value)
                                        .map(([k, v]) => `${k}: ${v}`)
                                        .join(', ');
                                }
                                // Handle arrays
                                else if (Array.isArray(value)) {
                                    value = value.join(', ');
                                }

                                return `<td style="padding: 8px; border: 1px solid #ddd;">${value ?? ''}</td>`;
                            }).join('')}
                        </tr>`).join('')}
                </tbody>
            </table>`;
    };

    // Check if response is a direct array
    if (Array.isArray(response) && response.length > 0) {
        this.messagesDiv.el.insertAdjacentHTML('beforeend', `<div class="overflow-auto">${createTable(response)}</div>`);
    }
    // Check if response is an object with nested data
    else if (typeof response === 'object' && response !== null) {
        let hasNestedData = false;

        for (const [key, value] of Object.entries(response)) {
            // Handle array of objects or array of primitives
            if (Array.isArray(value) && value.length > 0) {
                const firstNonNull = value.find(item => item !== null && item !== undefined);

                if (firstNonNull && typeof firstNonNull === 'object') {
                    // Array of objects - create a proper table
                    this.messagesDiv.el.insertAdjacentHTML('beforeend', `<h4 style="margin-top: 15px; margin-bottom: 10px;">${key.replace(/_/g, ' ').toUpperCase()}</h4>`);
                    this.messagesDiv.el.insertAdjacentHTML('beforeend', `<div class="overflow-auto">${createTable(value)}</div>`);
                } else {
                    // Array of primitives - simple table
                    const simpleTable = `
                        <table border="1" class="table" style="border-collapse: collapse; width: 100%;">
                            <thead style="background-color: #f2f2f2;">
                                <tr><th style="padding: 8px; border: 1px solid #ddd;">${key.toUpperCase().replace(/_/g, ' ')}</th></tr>
                            </thead>
                            <tbody>
                                ${value.filter(item => item !== null && item !== undefined).map(item => `
                                    <tr style="text-align: left;">
                                        <td style="padding: 8px; border: 1px solid #ddd;">${item}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    `;
                    this.messagesDiv.el.insertAdjacentHTML('beforeend', `<h4 style="margin-top: 15px; margin-bottom: 10px;">${key.replace(/_/g, ' ').toUpperCase()}</h4>`);
                    this.messagesDiv.el.insertAdjacentHTML('beforeend', `<div class="overflow-auto">${simpleTable}</div>`);
                }
                hasNestedData = true;
            }
            // Handle nested object (single dictionary)
            else if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
                this.messagesDiv.el.insertAdjacentHTML('beforeend', `<h4 style="margin-top: 15px; margin-bottom: 10px;">${key.replace(/_/g, ' ').toUpperCase()}</h4>`);
                this.messagesDiv.el.insertAdjacentHTML('beforeend', `<div class="overflow-auto">${createTable(value)}</div>`);
                hasNestedData = true;
            }
            // Handle primitive values
            else if (value !== null && value !== undefined) {
                this.messagesDiv.el.insertAdjacentHTML('beforeend', `
                    <div style="margin: 10px 0;">
                        <strong>${key.replace(/_/g, ' ').toUpperCase()}:</strong> ${value}
                    </div>
                `);
                hasNestedData = true;
            }
        }

        // If no nested data was found, treat the entire object as a single row table
        if (!hasNestedData) {
            this.messagesDiv.el.insertAdjacentHTML('beforeend', `<div class="overflow-auto">${createTable(response)}</div>`);
        }
    }
    // Handle plain text response
    else {
        const div = document.createElement('div');
        div.className = 'chat-container-child';
        div.innerHTML = `
            <button class="flex gap-1 items-center copy_button">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" class="icon-sm">
                    <path fill="currentColor" fill-rule="evenodd" d="M7 5a3 3 0 0 1 3-3h9a3 3 0 0 1 3 3v9a3 3 0 0 1-3 3h-2v2a3 3 0 0 1-3 3H5a3 3 0 0 1-3-3v-9a3 3 0 0 1 3-3h2zm2 2h5a3 3 0 0 1 3 3v5h2a1 1 0 0 0 1-1V5a1 1 0 0 0-1-1h-9a1 1 0 0 0-1 1zM5 9a1 1 0 0 0-1 1v9a1 1 0 0 0 1 1h9a1 1 0 0 0 1-1v-9a1 1 0 0 0-1-1z" clip-rule="evenodd"></path>
                </svg>Copy
            </button>
            <pre class="message-content">${response}</pre>
        `;

        const button = div.querySelector('.copy_button');
        button?.addEventListener('click', async () => {
            const text = div.querySelector('.message-content')?.textContent || '';
            if (browser.navigator.clipboard) {
                try {
                    await browser.navigator.clipboard.writeText(text);
                } catch (error) {
                    console.error("Clipboard access is not available:", error);
                }
            }
        });

        this.messagesDiv.el.appendChild(div);
    }
}

    appendUserMessage(message) {
        this.messagesDiv.el.insertAdjacentHTML(
            "beforeend",
            `
            <div class="user-message">
                <h4>${this.user.name}</h4>
                <div class="o-mail-Message-content o-min-width-0">${message}</div>
            </div>
        `
        );
    }

    createTable(data) {
        if (!Array.isArray(data)) {
            data = [data];
        }
        const keys = Object.keys(data[0] || {});
        const formatDate = (date) => DateTime.fromISO(date).toFormat("yyyy-MM-dd");

        return `
            <table border="1" class="table" style="border-collapse: collapse; width: 100%;">
                <thead style="background-color: #f2f2f2;">
                    <tr>
                        ${keys
                            .map(
                                (key) =>
                                    `<th style="padding: 8px; border: 1px solid #ddd;">${key
                                        .toUpperCase()
                                        .replace(/_/g, " ")}</th>`
                            )
                            .join("")}
                    </tr>
                </thead>
                <tbody>
                    ${data
                        .map(
                            (row) => `
                        <tr>
                            ${keys
                                .map((key) => {
                                    const value = row[key];
                                    const display = [
                                        "create_date",
                                        "date_order",
                                        "write_date",
                                    ].includes(key)
                                        ? formatDate(value)
                                        : value;
                                    return `<td style="padding: 8px; border: 1px solid #ddd;">${display}</td>`;
                                })
                                .join("")}
                        </tr>
                    `
                        )
                        .join("")}
                </tbody>
            </table>
        `;
    }

    async sendMessage() {
        const userMessage = this.messageInput.el.value;
        if (!userMessage.trim()) return;

        this.messagesDiv.el.insertAdjacentHTML('beforeend', `
            <div class="user-message">
                <h4>${this.user.name}</h4>
                <div class="o-mail-Message-content">${userMessage}</div>
            </div>
        `);

        if (this.messagesDiv.el.lastElementChild) {
            this.messagesDiv.el.lastElementChild.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }

        setTimeout(() => {
            this.state.isloading = true;
        }, 1000);

        this.messageInput.el.value = '';

        if (!this.state.chatbot_session_id) {
            this.state.chatbot_session_id = await this.orm.create("chatbot.session", [{
                name: userMessage,
                partner_id: this.user.partnerId
            }]);
            cookie.set('chatbot_session_id', this.state.chatbot_session_id);
        }

        const response = await this.orm.call("chatbot", "get_response", [[]], {
            input_data: userMessage,
            chatbot_session_id: this.state.chatbot_session_id
        });

        const formatDate = date => DateTime.fromISO(date).toFormat('yyyy-MM-dd');
        this.messagesDiv.el.insertAdjacentHTML('beforeend', '<h3>AI Bot</h3>');

        // Use the renderResponse method
        this.renderResponse(response, formatDate);

        if (this.messagesDiv.el.lastElementChild) {
            this.messagesDiv.el.lastElementChild.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
        this.state.isloading = false;
        this.refreshHistory();
    }

    onClickHistoryItem(ev, history_id) {
        this.loadSpecificHistory(history_id);
    }

    onKeyPress(ev) {
        if (ev.key === "Enter") {
            ev.preventDefault();
            this.sendMessage();
        }
    }

    async deleteHistory(ev, history_id) {
        ev.stopPropagation();
        if (!history_id) {
            return;
        }
        if (!confirm("Are you sure you want to delete this chat session?")) {
            return;
        }
        try {
            await this.orm.unlink("chatbot.session", [history_id]);
            if (this.state.chatbot_session_id === history_id) {
                this.state.chatbot_session_id = false;
                cookie.set("chatbot_session_id", "");
                $(this.messagesDiv.el).empty();
            }
            this.state.todayHistory = this.state.todayHistory.filter(
                (h) => h.id !== history_id
            );
            this.state.yesterdayHistory = this.state.yesterdayHistory.filter(
                (h) => h.id !== history_id
            );
            this.state.olderHistory = this.state.olderHistory.filter(
                (h) => h.id !== history_id
            );
        } catch (error) {
            console.error("Error deleting chat session:", error);
        }
    }


    async editHistory(ev, history) {
        ev.stopPropagation();
        const listItem = ev.currentTarget.closest(".history-item");
        if (!listItem) return;
        const textSpan = listItem.querySelector(".history-text");
        if (!textSpan) return;
        if (listItem.querySelector("input")) return;
        const input = document.createElement("input");
        input.type = "text";
        input.value = history.name;
        input.className = "form-control d-inline-block";
        input.style.width = "70%";
        textSpan.style.display = "none";
        textSpan.insertAdjacentElement("afterend", input);
        input.focus();
        const saveEdit = async () => {
            const newName = input.value.trim();
            if (newName && newName !== history.name) {
                try {
                    await this.orm.write("chatbot.session", [history.id], {name: newName});
                    await this.refreshHistory();
                } catch (error) {
                    console.error("Error updating session:", error);
                }
            }
            input.remove();
            textSpan.style.display = "inline";
        };

        input.addEventListener("keypress", (e) => {
            if (e.key === "Enter") saveEdit();
            if (e.key === "Escape") { // cancel on ESC
                input.remove();
                textSpan.style.display = "inline";
            }
        });
        input.addEventListener("blur", saveEdit);
    }


    async toggleSidebar() {
        const [sidebar, arrowIcon, chatRight, chat, header] =
            ['chatHistorySidebar', 'arrowIcon', '.chat-container-right', '.chat-container', '.chatbotHeader']
            .map(id => document.getElementById(id) || document.querySelector(id));
        const isHidden = sidebar.style.display === 'none' || !sidebar.style.display;
        sidebar.style.display = isHidden ? 'block' : 'none';
        if(isHidden) {
        }
        arrowIcon.classList.toggle('fa-angle-double-right', !isHidden);
        arrowIcon.classList.toggle('fa-angle-double-left', isHidden);
        [chatRight, chat].forEach(el => {
            el.classList.toggle('col-9', isHidden);
            el.classList.toggle('col-12', !isHidden);
        });
        chat.classList.toggle('justify-content-center', !isHidden);
        header.classList.toggle('justify-content-between', isHidden);
    }

}

ChatBot.template = "chatbot.layout";
registry.category("actions").add("chatbot_action", ChatBot);
