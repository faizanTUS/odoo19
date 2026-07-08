/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, useEffect, onWillUnmount } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { showRingCentralWidget, postMessageToRingCentralWidget } from "@ringcentral_integration/js/ringcentral_widget_helper";

export class RCPhoneSystray extends Component {
    static template = "ringcentral_integration.RCPhoneSystray";

    setup() {
        this.accessService = useService("ringcentral.access");
        this.callService = useService("ringcentral.call");
        this.notification = useService("notification");

        this.state = useState({
            loading: false,
            widgetVisible: false,
            userStatus: "Offline",
            showStatusDropdown: false,
            isLoggedIn: false,
            accessDenied: false,
        });

        this._isToggling = false;
        this._setupWidgetStateListener();
        this._checkWidgetVisibility();

        const onCallStateChange = () => {
            if (this.callService.lockWidgetOpen) {
                this._ensureWidgetStaysVisible();
            }
        };
        this.callService.bus.addEventListener("change", onCallStateChange);
        this._onCallStateChange = onCallStateChange;

        useEffect(() => {
            const handleClickOutside = (ev) => {
                if (this.state.showStatusDropdown && !ev.target.closest(".dropdown")) {
                    this.state.showStatusDropdown = false;
                }
            };
            document.addEventListener("click", handleClickOutside);
            return () => document.removeEventListener("click", handleClickOutside);
        });

        onWillUnmount(() => {
            if (this._messageListener) {
                window.removeEventListener("message", this._messageListener, true);
            }
            if (this._onCallStateChange) {
                this.callService.bus.removeEventListener("change", this._onCallStateChange);
            }
        });
    }

    _setupWidgetStateListener() {
        window.addEventListener("ringcentral-widget-visibility-changed", (event) => {
            this.state.widgetVisible = event.detail.visible;
        });

        this._messageListener = (event) => {
            const data = event.data;
            if (!data || typeof data !== "object") {
                return;
            }

            this.callService.updateFromMessage(data);

            if (this.callService.lockWidgetOpen) {
                this._ensureWidgetStaysVisible();
            }

            if (data.type === "rc-adapter-set-minimized" && data.minimized === true) {
                if (!this._isToggling && this.callService.lockWidgetOpen) {
                    event.stopPropagation();
                    event.stopImmediatePropagation();
                    this._ensureWidgetStaysVisible();
                    return false;
                }
            }

            if (
                data.type === "rc-adapter-login" ||
                data.type === "rc-adapter-authenticated" ||
                data.type === "rc-adapter-ready" ||
                (data.type === "rc-adapter-state-change" && data.loggedIn === true)
            ) {
                this.state.isLoggedIn = true;
            }
            if (
                data.type === "rc-adapter-logout" ||
                data.type === "rc-adapter-unauthenticated" ||
                (data.type === "rc-adapter-state-change" && data.loggedIn === false)
            ) {
                this.state.isLoggedIn = false;
                this.state.userStatus = "Offline";
            }
            if (
                data.type === "rc-adapter-presence" ||
                data.type === "rc-adapter-telephony" ||
                data.type === "rc-adapter-state-change" ||
                data.type === "rc-adapter-presence-update" ||
                data.type === "rc-adapter-call-state-change" ||
                data.type === "rc-adapter-call-start" ||
                data.type === "rc-adapter-call-ring-notify" ||
                data.type === "rc-adapter-call-end"
            ) {
                if (this.state.isLoggedIn || data.type.startsWith("rc-adapter-call")) {
                    this._updateUserStatus(data);
                }
            } else if (data.userStatus || data.presenceStatus || data.telephonyStatus || data.dndStatus) {
                if (this.state.isLoggedIn) {
                    this._updateUserStatus(data);
                }
            }
            if (data.loggedIn !== undefined) {
                this.state.isLoggedIn = data.loggedIn;
            }
        };
        window.addEventListener("message", this._messageListener, true);
    }

    _ensureWidgetStaysVisible() {
        showRingCentralWidget();
        this.state.widgetVisible = true;
    }

    _updateUserStatus(data) {
        let newStatus = "Offline";
        if (data.callStatus === "ringing" || data.status === "ringing" || data.telephonyStatus === "Ringing") {
            newStatus = "Ringing";
        } else if (
            data.callStatus === "active" ||
            data.status === "active" ||
            data.callStatus === "onCall" ||
            data.status === "onCall" ||
            data.telephonyStatus === "CallConnected" ||
            data.telephonyStatus === "OnHold"
        ) {
            newStatus = "OnCall";
        } else if (
            data.dndStatus === "DoNotAcceptAnyCalls" ||
            data.dndStatus === "DoNotAcceptDepartmentCalls"
        ) {
            newStatus = "DND";
        } else if (data.userStatus) {
            newStatus = data.userStatus;
        } else if (data.presenceStatus) {
            newStatus = data.presenceStatus;
        } else if (data.telephonyStatus === "NoCall") {
            newStatus = data.userStatus || data.presenceStatus || "Available";
        }

        if (newStatus === "Available" || newStatus === "available") {
            newStatus = "Available";
        } else if (newStatus === "Busy" || newStatus === "busy") {
            newStatus = "Busy";
        } else if (newStatus === "DoNotDisturb" || newStatus === "DND" || newStatus === "dnd") {
            newStatus = "DND";
        }
        if (this.state.userStatus !== newStatus) {
            this.state.userStatus = newStatus;
        }
    }

    _checkWidgetVisibility() {
        const widget = document.getElementById("rc-widget");
        if (widget) {
            const isVisible =
                widget.classList.contains("rc-widget-visible") ||
                (window.getComputedStyle(widget).display !== "none" &&
                    window.getComputedStyle(widget).visibility !== "hidden" &&
                    window.getComputedStyle(widget).opacity !== "0");
            this.state.widgetVisible = isVisible;
        } else {
            this.state.widgetVisible = false;
            this.state.isLoggedIn = false;
        }
    }

    async _fetchWidgetConfig() {
        try {
            const response = await fetch("/ringcentral/api/config", {
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
            if (!response.ok) {
                return null;
            }
            const payload = await response.json();
            const result = payload.result || payload;
            return result?.data || null;
        } catch (error) {
            console.warn("RingCentral: could not load widget config", error);
            return null;
        }
    }

    async _ensureAdapterScript() {
        if (document.querySelector('script[src*="ringcentral-embeddable"]')) {
            return true;
        }
        const config = await this._fetchWidgetConfig();
        let adapterUrl =
            "https://apps.ringcentral.com/integration/ringcentral-embeddable/latest/adapter.js";
        if (config?.client_id) {
            const server = config.server_url === "https://platform.ringcentral.com" ? "prod" : "dev";
            adapterUrl += `?clientId=${encodeURIComponent(config.client_id)}&appServer=${server}`;
        }
        this.state.loading = true;
        return new Promise((resolve) => {
            const script = document.createElement("script");
            script.src = adapterUrl;
            script.async = true;
            script.defer = true;
            script.onload = () => {
                this.state.loading = false;
                window.ringcentralAdapterReady = true;
                resolve(true);
            };
            script.onerror = () => {
                this.state.loading = false;
                console.error("RingCentral: failed to load embeddable adapter");
                resolve(false);
            };
            document.head.appendChild(script);
        });
    }

    async onClick(ev) {
        if (ev) {
            ev.preventDefault();
            ev.stopPropagation();
        }
        await this.accessService.refresh();
        if (!this.accessService.hasAccess) {
            this.notification.add(
                _t("RingCentral access denied. Contact your administrator to enable RingCentral for your company."),
                { type: "warning" }
            );
            this.state.accessDenied = true;
            return;
        }
        this.state.accessDenied = false;
        if (this.accessService.needsAdminConfig) {
            this.notification.add(
                _t("RingCentral company setup is incomplete. You can still sign in to the widget; ask your administrator to finish the RingCentral configuration for full features."),
                { type: "info" }
            );
        }
        try {
            const loaded = await this._ensureAdapterScript();
            if (!loaded) {
                this.notification.add(
                    _t("Could not load the RingCentral widget. Please try again or contact your administrator."),
                    { type: "danger" }
                );
                return;
            }
            setTimeout(() => this.toggleWidget(), 300);
        } catch (e) {
            this.state.loading = false;
            console.error("Error loading RingCentral widget:", e);
        }
    }

    toggleWidget() {
        if (this.callService.lockWidgetOpen && this.state.widgetVisible) {
            this._ensureWidgetStaysVisible();
            return;
        }
        this._isToggling = true;
        const widget = document.getElementById("rc-widget");
        if (!widget) {
            showRingCentralWidget();
            this._isToggling = false;
            return;
        }

        const isCurrentlyVisible =
            widget.classList.contains("rc-widget-visible") ||
            (window.getComputedStyle(widget).display !== "none" &&
                window.getComputedStyle(widget).visibility !== "hidden" &&
                window.getComputedStyle(widget).opacity !== "0");
        const shouldShow = !isCurrentlyVisible;

        try {
            if (shouldShow) {
                widget.style.cssText =
                    "display: block !important; visibility: visible !important; opacity: 1 !important; position: fixed !important; bottom: 20px !important; right: 20px !important; z-index: 1000 !important; max-width: 400px !important; max-height: 600px !important; pointer-events: auto !important;";
                widget.classList.add("rc-widget-visible");
                this.state.widgetVisible = true;
                postMessageToRingCentralWidget({ type: "rc-adapter-set-minimized", minimized: false });
                postMessageToRingCentralWidget({ type: "rc-adapter-open-dialer" });
            } else if (!this.callService.lockWidgetOpen) {
                widget.style.cssText =
                    "display: none !important; visibility: hidden !important; opacity: 0 !important; pointer-events: none !important;";
                widget.classList.remove("rc-widget-visible");
                this.state.widgetVisible = false;
                postMessageToRingCentralWidget({ type: "rc-adapter-set-minimized", minimized: true });
            }
        } catch (e) {
            console.error("Error toggling widget:", e);
        } finally {
            setTimeout(() => {
                this._isToggling = false;
            }, 500);
        }
    }

    onPhoneClick(ev) {
        if (ev) {
            ev.preventDefault();
            ev.stopPropagation();
        }
        this.state.showStatusDropdown = !this.state.showStatusDropdown;
    }

    setStatus(ev) {
        if (ev) {
            ev.preventDefault();
            ev.stopPropagation();
        }
        if (!this.state.isLoggedIn) {
            this.state.showStatusDropdown = false;
            return;
        }
        const status = ev.currentTarget.getAttribute("data-status");
        const dndStatus = ev.currentTarget.getAttribute("data-dnd");
        const widget = document.getElementById("rc-widget");
        if (widget) {
            postMessageToRingCentralWidget({
                type: "rc-adapter-set-presence",
                userStatus: status,
                dndStatus,
            });
            this._ensureWidgetStaysVisible();
        }
        if (dndStatus === "DoNotAcceptAnyCalls" || dndStatus === "DoNotAcceptDepartmentCalls") {
            this.state.userStatus = "DND";
        } else {
            this.state.userStatus = status;
        }
        this.state.showStatusDropdown = false;
    }

    get iconPath() {
        const baseUrl = window.location.origin;
        if (this.state.widgetVisible) {
            return `${baseUrl}/ringcentral_integration/static/src/img/rc_icon_visible.png`;
        }
        return `${baseUrl}/ringcentral_integration/static/src/img/rc_icon_hidden.svg`;
    }

    get statusColor() {
        const statusColors = {
            Available: "#28a745",
            Busy: "#dc3545",
            OnCall: "#ff9800",
            Ringing: "#ffc107",
            DND: "#6c757d",
            Offline: "#adb5bd",
        };
        return statusColors[this.state.userStatus] || statusColors.Offline;
    }

    get statusTitle() {
        return `RingCentral - ${this.state.userStatus}`;
    }

    get statusIconClass() {
        return this.state.userStatus === "DND" ? "fa fa-ban" : "fa fa-circle";
    }

    get statusIconStyle() {
        const color = this.statusColor || "#adb5bd";
        return `color: ${color} !important; font-size: 14px !important; display: inline-block !important;`;
    }
}

window.showRingCentralWidget = showRingCentralWidget;

registry.category("systray").add(
    "ringcentral_integration.RCPhoneSystray",
    {
        Component: RCPhoneSystray,
        isDisplayed(env) {
            const access = env.services["ringcentral.access"];
            return access ? access.hasAccess : false;
        },
    },
    { sequence: 99 }
);
