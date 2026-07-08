/** @odoo-module **/

/**
 * RingCentral Widget Helper
 * Provides utilities to show/hide the widget and handle click-to-call
 */

const SESSION_LOCK_KEY = "ringcentral.sessionLock";
const ACTIVE_CALL_KEY = "ringcentral.activeCall";

// Track if we're already showing the widget to avoid duplicate calls
let showingWidget = false;
let checkIntervalId = null;
let inboundWidgetSuppressed = false;
let suppressEnforceId = null;
let suppressEnforceStartedAt = 0;

const SUPPRESS_ENFORCE_MS = 250;
const SUPPRESS_MAX_LIFETIME_MS = 60000;

const WIDGET_HIDDEN_STYLE =
    "display: none !important; visibility: hidden !important; opacity: 0 !important; pointer-events: none !important;";

function enforceWidgetHidden() {
    const widget = document.getElementById("rc-widget");
    if (!widget) {
        return;
    }
    widget.style.cssText = WIDGET_HIDDEN_STYLE;
    widget.classList.remove("rc-widget-visible");
    window.dispatchEvent(
        new CustomEvent("ringcentral-widget-visibility-changed", {
            detail: { visible: false },
        })
    );
    postMessageToRingCentralWidget({ type: "rc-adapter-set-minimized", minimized: true });
}

function clearSuppressEnforceInterval() {
    if (suppressEnforceId) {
        clearInterval(suppressEnforceId);
        suppressEnforceId = null;
    }
    suppressEnforceStartedAt = 0;
}

/**
 * When true, the embeddable RC widget stays hidden (used by ringcentral_lead_creation
 * during inbound ringing so only the Odoo lead popup is shown).
 */
export function setInboundWidgetSuppressed(value) {
    inboundWidgetSuppressed = Boolean(value);
    if (inboundWidgetSuppressed) {
        enforceWidgetHidden();
        clearSuppressEnforceInterval();
        suppressEnforceStartedAt = Date.now();
        suppressEnforceId = setInterval(() => {
            if (!inboundWidgetSuppressed) {
                clearSuppressEnforceInterval();
                return;
            }
            if (Date.now() - suppressEnforceStartedAt > SUPPRESS_MAX_LIFETIME_MS) {
                setInboundWidgetSuppressed(false);
                return;
            }
            enforceWidgetHidden();
        }, SUPPRESS_ENFORCE_MS);
    } else {
        clearSuppressEnforceInterval();
    }
}

export function isInboundWidgetSuppressed() {
    return inboundWidgetSuppressed;
}

/** Hide the widget without enabling inbound suppression (e.g. after decline). */
export function hideRingCentralWidget() {
    enforceWidgetHidden();
}

function safeIframeWindow(iframe) {
    if (!iframe) {
        return null;
    }
    try {
        const contentWindow = iframe.contentWindow;
        if (contentWindow && typeof contentWindow.postMessage === "function") {
            return contentWindow;
        }
    } catch (_error) {
        // Cross-origin iframe; postMessage is not available from this context.
    }
    return null;
}

export function getRingCentralWidgetTargets() {
    const adapterFrame = document.querySelector("#rc-widget-adapter-frame");
    const widget = document.getElementById("rc-widget");
    const iframe = widget ? widget.querySelector("iframe") : null;
    const targets = [];
    const seen = new Set();
    for (const candidate of [
        safeIframeWindow(adapterFrame),
        safeIframeWindow(iframe),
        window,
    ]) {
        if (candidate && !seen.has(candidate)) {
            seen.add(candidate);
            targets.push(candidate);
        }
    }
    return targets;
}

export function postMessageToRingCentralWidget(message) {
    if (!message || typeof message !== "object") {
        return;
    }
    for (const target of getRingCentralWidgetTargets()) {
        try {
            target.postMessage(message, "*");
        } catch (_error) {
            // Ignore cross-origin postMessage failures.
        }
    }
}

export function showRingCentralWidget(options = {}) {
    /**
     * Show the RingCentral widget if it's hidden
     * Waits for widget to be ready if it doesn't exist yet
     * Debounced to prevent excessive calls
     */
    if (inboundWidgetSuppressed) {
        return;
    }

    // Prevent duplicate calls
    if (showingWidget) {
        return;
    }
    
    const openDialer = options.openDialer !== false;
    const showWidget = () => {
        const widget = document.getElementById("rc-widget");
        if (!widget) {
            return false;
        }

        // Check if already visible
        if (widget.classList.contains('rc-widget-visible')) {
            showingWidget = false;
            return true;
        }

        showingWidget = true;

        // Show widget with proper positioning
        widget.style.cssText = "display: block !important; visibility: visible !important; opacity: 1 !important; position: fixed !important; bottom: 20px !important; right: 20px !important; z-index: 1000 !important; max-width: 400px !important; max-height: 600px !important; pointer-events: auto !important;";
        widget.classList.add("rc-widget-visible");
        
        // Trigger custom event to notify systray of visibility change
        window.dispatchEvent(new CustomEvent('ringcentral-widget-visibility-changed', { 
            detail: { visible: true } 
        }));

        // Keep widget visible and optionally open dialer.
        postMessageToRingCentralWidget({ type: "rc-adapter-set-minimized", minimized: false });
        if (openDialer) {
            postMessageToRingCentralWidget({ type: "rc-adapter-open-dialer" });
        }
        
        // Reset flag after a short delay
        setTimeout(() => {
            showingWidget = false;
        }, 500);
        
        return true;
    };

    // Try immediately
    if (showWidget()) {
        return;
    }

    // If widget doesn't exist, wait for it (max 3 seconds, less frequent checks)
    let attempts = 0;
    const maxAttempts = 15; // 3 seconds with 200ms intervals (less frequent)
    
    // Clear any existing interval
    if (checkIntervalId) {
        clearInterval(checkIntervalId);
    }
    
    checkIntervalId = setInterval(() => {
        attempts++;
        if (showWidget() || attempts >= maxAttempts) {
            clearInterval(checkIntervalId);
            checkIntervalId = null;
            showingWidget = false;
        }
    }, 200); // Slower interval (200ms instead of 100ms)
}

export function setupClickToCall() {
    /**
     * Intercept tel: links and show widget when clicked
     * Optimized to prevent excessive event handling
     */
    let lastClickTime = 0;
    const CLICK_DEBOUNCE_MS = 500; // Prevent rapid clicks
    
    document.addEventListener('click', function(e) {
        const link = e.target.closest('a[href^="tel:"]');
        if (!link) {
            return;
        }
        
        // Debounce rapid clicks
        const now = Date.now();
        if (now - lastClickTime < CLICK_DEBOUNCE_MS) {
            e.preventDefault();
            return;
        }
        lastClickTime = now;
        
        e.preventDefault();
        const phoneNumber = link.getAttribute('href').replace('tel:', '');
        
        // Show widget first
        showRingCentralWidget();
        
        // Wait a bit for widget to be ready, then set the number (only once)
        setTimeout(() => {
            const widget = document.getElementById("rc-widget");
            if (!widget) {
                return;
            }
            
            const targets = getRingCentralWidgetTargets();
            
            // Send messages only once per target
            for (const target of targets) {
                postMessageToRingCentralWidget({
                    type: "rc-adapter-set-dialer-number",
                    phoneNumber: phoneNumber,
                });
            }
            
            // Try to initiate call after a short delay (only once)
            setTimeout(() => {
                postMessageToRingCentralWidget({
                    type: "rc-adapter-new-call",
                    phoneNumber: phoneNumber,
                });
            }, 200);
        }, 500);
    }, true); // Use capture phase to catch early
}

export function hasSessionLockFromStorage() {
    try {
        if (sessionStorage.getItem(SESSION_LOCK_KEY) === "1") {
            return true;
        }
        const raw = sessionStorage.getItem(ACTIVE_CALL_KEY);
        if (!raw) {
            return false;
        }
        const state = JSON.parse(raw);
        if (state?.updatedAt && Date.now() - state.updatedAt > 4 * 60 * 60 * 1000) {
            return false;
        }
        return Boolean(state?.status && state.status !== "idle");
    } catch {
        return false;
    }
}

function hasActiveCallFromStorage() {
    return hasSessionLockFromStorage();
}

export function disableWidgetMinimizeButton() {
    /**
     * Disable widget's own minimize button - we control visibility via systray only
     * Intercepts minimize messages and prevents widget from toggling itself
     */
    let checkCount = 0;
    const maxChecks = 30; // Check for 30 seconds after page load
    
    const disableMinimize = () => {
        const widget = document.getElementById("rc-widget");
        if (!widget) {
            checkCount++;
            if (checkCount < maxChecks) {
                setTimeout(disableMinimize, 1000);
            }
            return;
        }
        
        // Intercept postMessage to prevent widget from minimizing itself
        // This listener prevents the widget from hiding when status changes
        const messageInterceptor = (event) => {
            if (event.data && typeof event.data === 'object') {
                const data = event.data;
                if (data.type === 'rc-adapter-set-minimized' && data.minimized === true) {
                    if (inboundWidgetSuppressed) {
                        return;
                    }
                    if (hasActiveCallFromStorage()) {
                        event.stopPropagation();
                        event.stopImmediatePropagation();
                        showRingCentralWidget();
                        return false;
                    }
                }
            }
        };
        
        // Listen in capture phase to intercept early
        window.addEventListener('message', messageInterceptor, true);
        
        // Also intercept clicks on widget minimize buttons and presence/adapter elements
        const clickInterceptor = (e) => {
            const target = e.target;
            const widget = document.getElementById("rc-widget");
            
            // Check if widget is visible - if so, prevent any clicks that might hide it
            if (widget && widget.classList.contains('rc-widget-visible')) {
                // Prevent clicks on minimize/close buttons
                if (target && (
                    target.closest('[aria-label*="minimize" i]') ||
                    target.closest('[aria-label*="close" i]') ||
                    target.closest('[class*="minimize" i]') ||
                    target.closest('[class*="close" i]') ||
                    // Prevent clicks on presence/adapter header elements
                    target.closest('[class*="presence" i]') ||
                    target.closest('[class*="adapter" i]') ||
                    target.closest('[class*="Adapter" i]') ||
                    target.closest('[class*="Presence" i]') ||
                    target.closest('[aria-label*="presence" i]') ||
                    target.closest('[aria-label*="adapter" i]') ||
                    // Prevent clicks on header buttons that might toggle visibility
                    (target.closest('header') && target.closest('button')) ||
                    (target.closest('.rc-widget-header') && target.closest('button'))
                )) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    // Ensure widget stays visible
                    widget.style.cssText = "display: block !important; visibility: visible !important; opacity: 1 !important; position: fixed !important; bottom: 20px !important; right: 20px !important; z-index: 1000 !important; max-width: 400px !important; max-height: 600px !important; pointer-events: auto !important;";
                    widget.classList.add('rc-widget-visible');
                    return false;
                }
            }
        };
        
        widget.addEventListener('click', clickInterceptor, true);
        
        // Also intercept clicks on the widget container itself
        const widgetClickInterceptor = (e) => {
            const widget = document.getElementById("rc-widget");
            if (widget && widget.classList.contains('rc-widget-visible')) {
                // If clicking on header area, prevent default behavior
                if (e.target.closest('header') || e.target.closest('.rc-widget-header')) {
                    // Allow clicks inside the widget content, but prevent header clicks from hiding
                    const isPresenceOrAdapter = e.target.closest('[class*="presence" i]') ||
                                                e.target.closest('[class*="adapter" i]') ||
                                                e.target.closest('[class*="Adapter" i]') ||
                                                e.target.closest('[class*="Presence" i]');
                    if (isPresenceOrAdapter) {
                        e.preventDefault();
                        e.stopPropagation();
                        e.stopImmediatePropagation();
                        return false;
                    }
                }
            }
        };
        
        widget.addEventListener('click', widgetClickInterceptor, true);
        
        // Try to hide minimize button in iframe (if accessible)
        const hideMinimizeButton = () => {
            const iframe = widget.querySelector("iframe");
            if (iframe && iframe.contentWindow) {
                try {
                    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                    if (iframeDoc) {
                        const selectors = [
                            'button[aria-label*="minimize" i]',
                            'button[aria-label*="close" i]',
                            '[class*="minimize"]',
                            '[class*="Minimize"]'
                        ];
                        
                        selectors.forEach(selector => {
                            try {
                                const buttons = iframeDoc.querySelectorAll(selector);
                                buttons.forEach(btn => {
                                    const text = (btn.textContent || '').toLowerCase();
                                    const ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
                                    if (text.includes('minimize') || text.includes('close') || 
                                        ariaLabel.includes('minimize') || ariaLabel.includes('close')) {
                                        btn.style.display = 'none';
                                        btn.style.visibility = 'hidden';
                                        btn.style.pointerEvents = 'none';
                                        btn.setAttribute('disabled', 'true');
                                    }
                                });
                            } catch (e) {
                                // Selector might not be valid
                            }
                        });
                    }
                } catch (e) {
                    // Cross-origin, can't access iframe content
                }
            }
        };
        
        // Hide button immediately and periodically
        hideMinimizeButton();
        const hideInterval = setInterval(hideMinimizeButton, 2000);
        setTimeout(() => clearInterval(hideInterval), 30000);
    };
    
    // Start after a delay
    setTimeout(disableMinimize, 2000);
}

// Auto-setup when module loads and Odoo is ready
// Wait for Odoo to be fully initialized before setting up listeners
if (document.readyState === 'complete') {
    setTimeout(() => {
        setupClickToCall();
        disableWidgetMinimizeButton();
    }, 1000);
} else {
    window.addEventListener('load', () => {
        setTimeout(() => {
            setupClickToCall();
            disableWidgetMinimizeButton();
        }, 1000);
    });
}

