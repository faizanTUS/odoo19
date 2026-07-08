/** @odoo-module **/

import { registry } from "@web/core/registry";
import { EventBus } from "@odoo/owl";
import { showRingCentralWidget } from "@ringcentral_integration/js/ringcentral_widget_helper";

const STORAGE_KEY = "ringcentral.activeCall";
const SESSION_LOCK_KEY = "ringcentral.sessionLock";
const STORAGE_TTL_MS = 4 * 60 * 60 * 1000; // 4 hours
const WATCHDOG_INTERVAL_MS = 1000;

const ACTIVE_STATUSES = new Set([
    "initiated",
    "dialing",
    "ringing",
    "incoming",
    "active",
    "onhold",
    "hold",
    "transfer",
    "oncall",
]);

const CALL_MESSAGE_TYPES = new Set([
    "rc-adapter-call-start",
    "rc-adapter-call-ring-notify",
    "rc-adapter-call-end",
    "rc-adapter-call-state-change",
    "rc-adapter-new-call",
    "rc-adapter-outbound-call",
    "rc-adapter-inbound-call",
    "rc-call-ring-notify",
    "rc-call-start-notify",
    "rc-call-end-notify",
    "rc-adapter-presence",
    "rc-adapter-telephony",
    "rc-adapter-state-change",
]);

const CALL_START_TYPES = new Set([
    "rc-adapter-call-start",
    "rc-adapter-call-ring-notify",
    "rc-adapter-new-call",
    "rc-adapter-outbound-call",
    "rc-adapter-inbound-call",
]);

const OUTBOUND_START_TYPES = new Set([
    "rc-adapter-outbound-call",
]);

function readStoredState() {
    try {
        const raw = sessionStorage.getItem(STORAGE_KEY);
        if (!raw) {
            return null;
        }
        const state = JSON.parse(raw);
        if (state?.updatedAt && Date.now() - state.updatedAt > STORAGE_TTL_MS) {
            sessionStorage.removeItem(STORAGE_KEY);
            sessionStorage.removeItem(SESSION_LOCK_KEY);
            return null;
        }
        return state;
    } catch {
        return null;
    }
}

function writeStoredState(state) {
    try {
        if (!state || state.status === "idle") {
            sessionStorage.removeItem(STORAGE_KEY);
            return;
        }
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch {
        // Ignore storage failures.
    }
}

function readSessionLock() {
    try {
        return sessionStorage.getItem(SESSION_LOCK_KEY) === "1";
    } catch {
        return false;
    }
}

function writeSessionLock(locked) {
    try {
        if (locked) {
            sessionStorage.setItem(SESSION_LOCK_KEY, "1");
        } else {
            sessionStorage.removeItem(SESSION_LOCK_KEY);
        }
    } catch {
        // Ignore storage failures.
    }
}

export function hasSessionLockFromStorage() {
    return readSessionLock() || hasActiveCallFromStorage();
}

async function reportCallEvent(event, phoneNumber, sessionId, direction, callerName = null) {
    try {
        const response = await fetch("/ringcentral/api/call-event", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {
                    event,
                    phone_number: phoneNumber || null,
                    session_id: sessionId || null,
                    direction: direction || "outbound",
                    caller_name: callerName || null,
                },
                id: Math.floor(Math.random() * 1000000),
            }),
        });
        if (!response.ok) {
            console.warn("RingCentral call-event HTTP error:", response.status);
        }
    } catch (error) {
        console.warn("RingCentral call-event failed:", error);
    }
}

function extractWidgetCallId(data) {
    if (!data || typeof data !== "object") {
        return null;
    }
    const call = data.call;
    if (call && typeof call === "object" && call.id) {
        return String(call.id);
    }
    if (data.callId) {
        return String(data.callId);
    }
    return null;
}

function extractSessionId(data, state = null) {
    if (!data || typeof data !== "object") {
        return state?.sessionId || null;
    }
    const session = data.telephonySession;
    const call = data.call;
    const candidates = [
        data.telephonySessionId,
        data.sessionId,
        call?.telephonySessionId,
        call?.sessionId,
        session?.telephonySessionId,
        session?.sessionId,
        state?.sessionId,
    ];
    for (const value of candidates) {
        if (value) {
            return String(value);
        }
    }
    return null;
}

function extractIncomingCaller(data) {
    if (!data || typeof data !== "object") {
        return { phoneNumber: null, callerName: null };
    }
    const call = data.call;
    if (call && typeof call === "object") {
        const from = call.from;
        if (from && typeof from === "object") {
            return {
                phoneNumber: from.phoneNumber || from.phone_number || from.number || null,
                callerName: from.name || from.displayName || null,
            };
        }
        return {
            phoneNumber: call.fromNumber || call.from_number || null,
            callerName: call.fromName || call.callerName || null,
        };
    }
    const session = data.telephonySession;
    if (session && typeof session === "object") {
        const parties = session.parties || session.party || [];
        const arr = Array.isArray(parties) ? parties : [parties];
        let fallbackCaller = null;
        for (const party of arr) {
            const direction = (party.direction || "").toLowerCase();
            if (direction !== "inbound" && direction !== "incoming") {
                continue;
            }
            const from = party.from || {};
            let phoneNumber = null;
            let callerName = null;
            if (typeof from === "object") {
                phoneNumber = from.phoneNumber || from.phone_number || party.phoneNumber || null;
                callerName = from.name || party.name || null;
            } else {
                phoneNumber = party.phoneNumber || null;
                callerName = party.name || null;
            }
            if (!fallbackCaller && phoneNumber) {
                fallbackCaller = { phoneNumber, callerName };
            }
            if (phoneNumber && isExternalPstnNumber(phoneNumber)) {
                return { phoneNumber, callerName };
            }
        }
        if (fallbackCaller) {
            return fallbackCaller;
        }
    }
    const fallbackNumber = data.phoneNumber || data.fromNumber || null;
    return {
        phoneNumber: fallbackNumber,
        callerName: data.callerName || null,
    };
}

function extractCallDirection(data) {
    if (!data || typeof data !== "object") {
        return "";
    }
    const call = data.call || {};
    const candidates = [
        data.direction,
        call.direction,
        data.telephonySession?.direction,
    ];
    for (const value of candidates) {
        if (value) {
            return String(value).toLowerCase();
        }
    }
    const type = data.type || "";
    if (type === "rc-adapter-outbound-call" || OUTBOUND_START_TYPES.has(type)) {
        return "outbound";
    }
    if (type === "rc-adapter-inbound-call") {
        return "inbound";
    }
    return "";
}

function isOutboundEvent(data) {
    const direction = extractCallDirection(data);
    return direction === "outbound" || direction === "outgoing";
}

function isExtensionNumber(number) {
    if (!number) {
        return false;
    }
    const stripped = String(number).trim();
    if (stripped.startsWith("+")) {
        return false;
    }
    const digits = stripped.replace(/\D/g, "");
    return digits.length > 0 && digits.length <= 6;
}

function isExternalPstnNumber(number) {
    if (!number || isExtensionNumber(number)) {
        return false;
    }
    const digits = String(number).replace(/\D/g, "");
    return digits.length >= 7;
}

function extractFromNumber(data) {
    if (!data || typeof data !== "object") {
        return null;
    }
    const call = data.call;
    if (call && typeof call === "object") {
        const from = call.from;
        if (from && typeof from === "object") {
            return from.phoneNumber || from.extensionNumber || from.number || null;
        }
        if (typeof from === "string") {
            return from;
        }
        return call.fromNumber || call.from_number || null;
    }
    const session = data.telephonySession;
    if (session && typeof session === "object") {
        const parties = session.parties || session.party || [];
        const arr = Array.isArray(parties) ? parties : [parties];
        for (const party of arr) {
            const partyDirection = String(party.direction || "").toLowerCase();
            if (partyDirection === "inbound" || partyDirection === "incoming") {
                const from = party.from || {};
                if (typeof from === "object") {
                    return from.phoneNumber || from.extensionNumber || party.phoneNumber || null;
                }
                return party.phoneNumber || null;
            }
        }
    }
    return data.fromNumber || data.phoneNumber || null;
}

function extractToNumber(data) {
    if (!data || typeof data !== "object") {
        return null;
    }
    const call = data.call;
    if (call && typeof call === "object") {
        const to = call.to;
        if (to && typeof to === "object") {
            return to.phoneNumber || to.extensionNumber || to.number || null;
        }
        if (typeof to === "string") {
            return to;
        }
        return call.toNumber || call.to_number || null;
    }
    const session = data.telephonySession;
    if (session && typeof session === "object") {
        const parties = session.parties || session.party || [];
        const arr = Array.isArray(parties) ? parties : [parties];
        for (const party of arr) {
            const partyDirection = String(party.direction || "").toLowerCase();
            if (partyDirection === "outbound" || partyDirection === "outgoing") {
                const to = party.to || {};
                if (typeof to === "object") {
                    return to.phoneNumber || to.extensionNumber || party.phoneNumber || null;
                }
                return party.phoneNumber || null;
            }
        }
    }
    return data.toNumber || data.to || data.phoneNumber || data.number || null;
}

function isClickToCallOutbound(data) {
    const type = data.type || "";
    if (type !== "rc-adapter-new-call" && type !== "rc-adapter-call-start") {
        return false;
    }
    const direction = extractCallDirection(data);
    if (direction === "inbound" || direction === "incoming") {
        return false;
    }
    return Boolean(data.phoneNumber || data.to || data.number);
}

function isExplicitOutboundEvent(data) {
    const type = data.type || "";
    if (type === "rc-adapter-outbound-call" || OUTBOUND_START_TYPES.has(type)) {
        return true;
    }
    if (isOutboundEvent(data)) {
        return true;
    }
    return isClickToCallOutbound(data);
}

function isRingNotifyInbound(data) {
    const direction = extractCallDirection(data);
    if (direction === "outbound" || direction === "outgoing") {
        return false;
    }
    if (direction === "inbound" || direction === "incoming") {
        return true;
    }
    const fromNumber = extractFromNumber(data);
    const toNumber = extractToNumber(data);
    const dialNumber = data.phoneNumber || data.to || data.number || null;
    if (dialNumber && toNumber && dialNumber === toNumber) {
        return false;
    }
    if (
        fromNumber && toNumber
        && isExternalPstnNumber(fromNumber)
        && isExternalPstnNumber(toNumber)
    ) {
        return false;
    }
    return Boolean(fromNumber && isExternalPstnNumber(fromNumber));
}

function hasInboundTelephonySession(data) {
    const session = data.telephonySession;
    if (!session || typeof session !== "object") {
        return false;
    }
    const parties = session.parties || session.party || [];
    const arr = Array.isArray(parties) ? parties : [parties];
    for (const party of arr) {
        const direction = String(party.direction || "").toLowerCase();
        if (direction !== "inbound" && direction !== "incoming") {
            continue;
        }
        const from = party.from || {};
        const phoneNumber = typeof from === "object"
            ? (from.phoneNumber || from.phone_number || party.phoneNumber)
            : party.phoneNumber;
        if (phoneNumber && isExternalPstnNumber(phoneNumber)) {
            return true;
        }
    }
    return false;
}

function isInboundRingingEvent(data) {
    if (!data || typeof data !== "object") {
        return false;
    }
    const type = data.type || "";
    if (isExplicitOutboundEvent(data)) {
        return false;
    }
    if (type === "rc-adapter-inbound-call") {
        return true;
    }
    if (type === "rc-call-ring-notify" || type === "rc-adapter-call-ring-notify") {
        return isRingNotifyInbound(data);
    }
    if (type === "rc-adapter-telephony" || type === "rc-adapter-presence") {
        if (!hasInboundTelephonySession(data)) {
            return false;
        }
        const telephonyStatus = String(
            data.telephonyStatus || data.call?.status || data.callStatus || ""
        ).toLowerCase();
        if (
            telephonyStatus === "nocal"
            || telephonyStatus === "callconnected"
            || telephonyStatus === "onhold"
            || telephonyStatus === "active"
            || telephonyStatus === "connected"
        ) {
            return false;
        }
        return true;
    }
    const direction = extractCallDirection(data);
    const status = String(
        data.status || data.call?.status || data.callStatus || data.telephonyStatus || ""
    ).toLowerCase();
    if (direction !== "inbound" && direction !== "incoming") {
        return false;
    }
    if (status && status !== "ringing" && status !== "proceeding") {
        return false;
    }
    const fromNumber = extractFromNumber(data);
    if (fromNumber && isExtensionNumber(fromNumber)) {
        return false;
    }
    if (fromNumber && isExternalPstnNumber(fromNumber)) {
        return true;
    }
    return true;
}

function normalizeStatus(data, sessionLock) {
    const type = data.type || "";
    if (type === "rc-adapter-call-end" || type === "rc-call-end-notify") {
        return "idle";
    }

    const candidates = [data.callStatus, data.status, data.telephonyStatus].filter(Boolean);
    for (const value of candidates) {
        const normalized = String(value);
        if (normalized === "CallConnected") {
            return "active";
        }
        if (normalized === "OnHold") {
            return "hold";
        }
        const lower = normalized.toLowerCase();
        if (ACTIVE_STATUSES.has(lower)) {
            if (lower === "oncall") {
                return "active";
            }
            if (lower === "ringing" || normalized === "Ringing") {
                return "ringing";
            }
            return lower;
        }
        if (normalized === "NoCall" && sessionLock) {
            return null;
        }
    }

    if (CALL_START_TYPES.has(type)) {
        return "ringing";
    }
    if (type.includes("transfer")) {
        return "transfer";
    }
    if (type.includes("hold")) {
        return "hold";
    }

    if (type === "rc-adapter-presence" || type === "rc-adapter-telephony") {
        const call = data.call || {};
        const callStatus = call.status || data.callStatus;
        if (callStatus === "ringing" || callStatus === "Ringing") {
            return "ringing";
        }
        if (callStatus === "active" || callStatus === "connected") {
            return "active";
        }
        if (callStatus === "NoCall" && sessionLock) {
            return null;
        }
    }

    return null;
}

function isRelevantMessage(data) {
    const type = data.type || "";
    if (type.startsWith("rc-adapter-call")) {
        return true;
    }
    if (CALL_MESSAGE_TYPES.has(type)) {
        return true;
    }
    if (type.includes("transfer") || type.includes("hold")) {
        return true;
    }
    return false;
}

export function hasActiveCallFromStorage() {
    try {
        const state = readStoredState();
        return Boolean(state?.status && state.status !== "idle");
    } catch {
        return false;
    }
}

export const ringcentralCallService = {
    start() {
        const bus = new EventBus();
        let state = readStoredState() || { status: "idle", sessionId: null, updatedAt: null };
        let sessionLock = readSessionLock();
        let deferInboundDialer = false;
        let watchdogId = null;
        const reportedOutboundSessions = new Set();
        const reportedInboundSessions = new Set();

        const persist = () => writeStoredState(state);

        const notifyChange = () => {
            bus.trigger("change", { ...state, sessionLock });
            window.dispatchEvent(
                new CustomEvent("ringcentral-call-state-changed", {
                    detail: { ...state, sessionLock },
                })
            );
        };

        const applyActiveCallUi = (options = {}) => {
            showRingCentralWidget(options);
        };

        const startWatchdog = () => {
            if (watchdogId) {
                return;
            }
            watchdogId = setInterval(() => {
                if (sessionLock || hasActiveCall()) {
                    applyActiveCallUi();
                } else {
                    stopWatchdog();
                }
            }, WATCHDOG_INTERVAL_MS);
        };

        const stopWatchdog = () => {
            if (watchdogId) {
                clearInterval(watchdogId);
                watchdogId = null;
            }
        };

        const setSessionLock = (locked) => {
            sessionLock = locked;
            writeSessionLock(locked);
            if (locked) {
                startWatchdog();
            } else {
                stopWatchdog();
            }
        };

        const hasActiveCall = () => {
            const status = String(state.status || "idle").toLowerCase();
            return ACTIVE_STATUSES.has(status);
        };

        const maybeReportOutboundStart = (data) => {
            const type = data.type || "";
            const isOutboundStart =
                OUTBOUND_START_TYPES.has(type) ||
                isClickToCallOutbound(data) ||
                (type === "rc-adapter-new-call" && isOutboundEvent(data));
            if (!isOutboundStart) {
                return;
            }
            const phoneNumber = data.phoneNumber || data.to || data.number || null;
            const sessionId = extractSessionId(data, state);
            const widgetCallId = extractWidgetCallId(data);
            const dedupeKey = sessionId || widgetCallId;
            if (!dedupeKey || reportedOutboundSessions.has(dedupeKey)) {
                return;
            }
            reportedOutboundSessions.add(dedupeKey);
            if (sessionId) {
                reportedOutboundSessions.add(sessionId);
            }
            if (widgetCallId) {
                reportedOutboundSessions.add(widgetCallId);
            }
            reportCallEvent("outbound_start", phoneNumber, sessionId, "outbound");
        };

        const isSuppressedOutboundSession = (sessionId, widgetCallId) => {
            const keys = [sessionId, widgetCallId].filter(Boolean);
            return keys.some((key) => reportedOutboundSessions.has(String(key)));
        };

        const updateFromMessage = (data) => {
            if (!data || typeof data !== "object") {
                return state;
            }

            const type = data.type || "";
            const sessionId = extractSessionId(data, state);
            const widgetCallId = extractWidgetCallId(data);

            maybeReportOutboundStart(data);

            if (isInboundRingingEvent(data)) {
                const caller = extractIncomingCaller(data);
                const suppressed =
                    isExplicitOutboundEvent(data)
                    || isSuppressedOutboundSession(sessionId, widgetCallId);
                if (!suppressed) {
                    const inboundKey = widgetCallId || sessionId || `${caller.phoneNumber || "unknown"}:${type}`;
                    if (!reportedInboundSessions.has(inboundKey)) {
                        reportedInboundSessions.add(inboundKey);
                        if (sessionId) {
                            reportedInboundSessions.add(sessionId);
                        }
                        if (widgetCallId) {
                            reportedInboundSessions.add(widgetCallId);
                        }
                        reportCallEvent(
                            "inbound_ring",
                            caller.phoneNumber,
                            sessionId,
                            "inbound",
                            caller.callerName
                        );
                    }
                    bus.trigger("inbound-ring", {
                        sessionId,
                        widgetCallId,
                        phoneNumber: caller.phoneNumber,
                        callerName: caller.callerName,
                        payload: data,
                    });
                    if (deferInboundDialer) {
                        return state;
                    }
                }
            }
            if (type === "rc-call-start-notify") {
                setSessionLock(true);
                state = {
                    status: "active",
                    sessionId: sessionId || state.sessionId || null,
                    widgetCallId: widgetCallId || state.widgetCallId || null,
                    updatedAt: Date.now(),
                };
                persist();
                applyActiveCallUi({ openDialer: true });
                notifyChange();
                return state;
            }
            if (CALL_START_TYPES.has(type)) {
                setSessionLock(true);
            }

            if (type === "rc-adapter-call-end" || type === "rc-call-end-notify") {
                if (sessionId) {
                    reportCallEvent("call_end", null, sessionId, null);
                }
                setSessionLock(false);
                reportedOutboundSessions.clear();
                reportedInboundSessions.clear();
                bus.trigger("call-ended", {
                    sessionId: sessionId || state.sessionId || null,
                    widgetCallId: widgetCallId || state.widgetCallId || null,
                });
            }

            const nextStatus = normalizeStatus(data, sessionLock);
            if (!nextStatus) {
                if (sessionLock) {
                    applyActiveCallUi();
                }
                return state;
            }

            if (nextStatus === "idle" && sessionLock) {
                applyActiveCallUi();
                return state;
            }

            const prevStatus = state.status;
            state = {
                status: nextStatus,
                sessionId: extractSessionId(data, state) || state.sessionId || null,
                widgetCallId: widgetCallId || state.widgetCallId || null,
                updatedAt: Date.now(),
            };
            persist();

            if (nextStatus === "idle") {
                setSessionLock(false);
                reportedOutboundSessions.clear();
            } else if (!sessionLock) {
                setSessionLock(true);
            }

            if (nextStatus !== "idle") {
                applyActiveCallUi();
            } else if (nextStatus !== prevStatus) {
                applyActiveCallUi();
            }
            notifyChange();
            return state;
        };

        const messageListener = (event) => {
            if (!event?.data || typeof event.data !== "object") {
                return;
            }
            const data = event.data;
            if (!isRelevantMessage(data)) {
                return;
            }
            updateFromMessage(data);

            if (
                data.type === "rc-adapter-set-minimized" &&
                data.minimized === true &&
                (sessionLock || state.status !== "idle")
            ) {
                event.stopPropagation();
                event.stopImmediatePropagation();
                applyActiveCallUi();
            }
        };
        window.addEventListener("message", messageListener, true);

        if (sessionLock || (state.status && state.status !== "idle")) {
            if (!sessionLock && state.status !== "idle") {
                setSessionLock(true);
            }
            applyActiveCallUi();
        }

        return {
            bus,
            setDeferInboundDialer(value) {
                deferInboundDialer = Boolean(value);
            },
            openDialer() {
                applyActiveCallUi({ openDialer: true });
            },
            activateAcceptedCall(sessionId = null, widgetCallId = null) {
                deferInboundDialer = false;
                setSessionLock(true);
                state = {
                    status: "active",
                    sessionId: sessionId || state.sessionId || null,
                    widgetCallId: widgetCallId || state.widgetCallId || null,
                    updatedAt: Date.now(),
                };
                persist();
                notifyChange();
                applyActiveCallUi({ openDialer: true });
            },
            get status() {
                return state.status;
            },
            get sessionLock() {
                return sessionLock;
            },
            get hasActiveCall() {
                return hasActiveCall();
            },
            get lockWidgetOpen() {
                return sessionLock || hasActiveCall();
            },
            isOutboundSession(sessionId) {
                if (!sessionId) {
                    return false;
                }
                return reportedOutboundSessions.has(String(sessionId));
            },
            isInboundSession(sessionId) {
                if (!sessionId) {
                    return false;
                }
                return reportedInboundSessions.has(String(sessionId));
            },
            registerInboundSession(sessionId = null, widgetCallId = null, phoneNumber = null) {
                if (sessionId) {
                    reportedInboundSessions.add(String(sessionId));
                }
                if (widgetCallId) {
                    reportedInboundSessions.add(String(widgetCallId));
                }
                if (phoneNumber) {
                    reportedInboundSessions.add(String(phoneNumber));
                }
            },
            updateFromMessage,
            clear() {
                setSessionLock(false);
                reportedOutboundSessions.clear();
                reportedInboundSessions.clear();
                state = { status: "idle", sessionId: null, updatedAt: Date.now() };
                persist();
                notifyChange();
            },
            destroy() {
                stopWatchdog();
                window.removeEventListener("message", messageListener, true);
            },
        };
    },
};

registry.category("services").add("ringcentral.call", ringcentralCallService);
