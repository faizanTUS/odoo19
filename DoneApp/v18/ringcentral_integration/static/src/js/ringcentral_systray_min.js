/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, useEffect } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { showRingCentralWidget } from "@ringcentral_integration/js/ringcentral_widget_helper";

export class RCPhoneSystray extends Component {
    static template = "ringcentral_integration.RCPhoneSystray";

    setup() {
        this.state = useState({
            loading: false,
            widgetVisible: false,
            userStatus: 'Offline', // Available, Busy, OnCall, DND, Offline, Ringing
            showStatusDropdown: false,
            isLoggedIn: false, // Track if user is logged in to RingCentral widget
        });
        
        // Track if we're toggling (to distinguish from widget's own minimize)
        this._isToggling = false;
        
        // Listen to widget state changes to update icon
        this._setupWidgetStateListener();
        // Check initial state
        this._checkWidgetVisibility();
        // Prevent widget clicks from toggling
        this._preventWidgetToggle();
        
        // Close dropdown when clicking outside
        useEffect(() => {
            const handleClickOutside = (ev) => {
                if (this.state.showStatusDropdown && 
                    !ev.target.closest('.dropdown')) {
                    this.state.showStatusDropdown = false;
                }
            };
            document.addEventListener('click', handleClickOutside);
            return () => {
                document.removeEventListener('click', handleClickOutside);
            };
        });
    }

    _setupWidgetStateListener() {
        // Listen for custom events from widget helper
        window.addEventListener('ringcentral-widget-visibility-changed', (event) => {
            this.state.widgetVisible = event.detail.visible;
        });
        
        // Listen for RingCentral presence/status events from widget
        this._messageListener = (event) => {
            if (event.data && typeof event.data === 'object') {
                const data = event.data;
                
                // IMPORTANT: Prevent widget from hiding when status changes
                // Intercept any minimize messages that might come from status changes
                // We only allow minimize from our systray toggle, not from widget itself
                if (data.type === 'rc-adapter-set-minimized' && data.minimized === true) {
                    const widget = document.getElementById("rc-widget");
                    // If widget is marked as visible and we're not toggling, prevent minimize
                    if (widget && this.state.widgetVisible && !this._isToggling) {
                        // This is a minimize request from widget itself (not from our systray)
                        // Don't process this minimize - widget should stay visible
                        event.stopPropagation();
                        event.stopImmediatePropagation();
                        // Ensure widget stays visible
                        this._ensureWidgetStaysVisible();
                        return false;
                    }
                }
                
                // Check for authentication/login events
                if (data.type === 'rc-adapter-login' || 
                    data.type === 'rc-adapter-authenticated' ||
                    data.type === 'rc-adapter-ready' ||
                    (data.type === 'rc-adapter-state-change' && data.loggedIn === true)) {
                    this.state.isLoggedIn = true;
                }
                
                // Check for logout events
                if (data.type === 'rc-adapter-logout' || 
                    data.type === 'rc-adapter-unauthenticated' ||
                    (data.type === 'rc-adapter-state-change' && data.loggedIn === false)) {
                    this.state.isLoggedIn = false;
                    this.state.userStatus = 'Offline';
                }
                
                // Handle presence events - check for all possible event types
                if (data.type === 'rc-adapter-presence' || 
                    data.type === 'rc-adapter-telephony' ||
                    data.type === 'rc-adapter-state-change' ||
                    data.type === 'rc-adapter-presence-update') {
                    // Only update status if logged in
                    if (this.state.isLoggedIn) {
                        this._updateUserStatus(data);
                        // Ensure widget stays visible when status changes
                        this._ensureWidgetStaysVisible();
                    }
                }
                // Handle call state changes
                else if (data.type === 'rc-adapter-call-state-change' || 
                         data.type === 'rc-adapter-call-start' ||
                         data.type === 'rc-adapter-call-ring-notify' ||
                         data.type === 'rc-adapter-call-end') {
                    this._updateUserStatus(data);
                    // Ensure widget stays visible during calls
                    this._ensureWidgetStaysVisible();
                }
                // Also check for status in any message
                else if (data.userStatus || data.presenceStatus || data.telephonyStatus || data.dndStatus) {
                    // Only update status if logged in
                    if (this.state.isLoggedIn) {
                        this._updateUserStatus(data);
                        // Ensure widget stays visible when status updates
                        this._ensureWidgetStaysVisible();
                    }
                }
                
                // Check for loggedIn status in any message
                if (data.loggedIn !== undefined) {
                    this.state.isLoggedIn = data.loggedIn;
                }
            }
        };
        
        window.addEventListener('message', this._messageListener, true); // Use capture phase
        
        // Also check widget visibility periodically to update icon (fallback)
        this._visibilityCheckInterval = setInterval(() => {
            this._checkWidgetVisibility();
        }, 1000); // Check every second
    }

    _ensureWidgetStaysVisible() {
        // Ensure widget doesn't hide when status changes
        const widget = document.getElementById("rc-widget");
        if (widget && this.state.widgetVisible) {
            // If widget should be visible, ensure it stays visible
            if (!widget.classList.contains('rc-widget-visible')) {
                widget.classList.add('rc-widget-visible');
            }
            if (window.getComputedStyle(widget).display === 'none') {
                widget.style.cssText = "display: block !important; visibility: visible !important; opacity: 1 !important; position: fixed !important; bottom: 20px !important; right: 20px !important; z-index: 1000 !important; max-width: 400px !important; max-height: 600px !important; pointer-events: auto !important;";
            }
        }
    }

    _preventWidgetToggle() {
        // Prevent widget's own minimize/maximize buttons and presence/adapter clicks from working
        // Intercept clicks on the widget
        const preventWidgetClicks = () => {
            const widget = document.getElementById("rc-widget");
            if (widget) {
                // Prevent clicks on minimize buttons and presence/adapter elements
                widget.addEventListener('click', (e) => {
                    // Check if widget is visible - if so, prevent any clicks that might hide it
                    if (!widget.classList.contains('rc-widget-visible')) {
                        return; // Allow clicks when widget is hidden
                    }
                    
                    const target = e.target;
                    if (target && (
                        // Minimize/close buttons
                        target.closest('[aria-label*="minimize" i]') ||
                        target.closest('[aria-label*="close" i]') ||
                        target.closest('[class*="minimize" i]') ||
                        target.closest('[class*="close" i]') ||
                        // Presence/adapter header elements
                        target.closest('[class*="presence" i]') ||
                        target.closest('[class*="adapter" i]') ||
                        target.closest('[class*="Adapter" i]') ||
                        target.closest('[class*="Presence" i]') ||
                        target.closest('[aria-label*="presence" i]') ||
                        target.closest('[aria-label*="adapter" i]') ||
                        // Header buttons that might toggle visibility
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
                }, true); // Use capture phase
            } else {
                // Retry after a delay
                setTimeout(preventWidgetClicks, 1000);
            }
        };
        
        setTimeout(preventWidgetClicks, 2000);
    }

    _updateUserStatus(data) {
        let newStatus = 'Offline';
        
        // Check for call status first (highest priority)
        if (data.callStatus === 'ringing' || data.status === 'ringing' || 
            data.telephonyStatus === 'Ringing') {
            newStatus = 'Ringing';
        } else if (data.callStatus === 'active' || data.status === 'active' || 
                   data.callStatus === 'onCall' || data.status === 'onCall' ||
                   data.telephonyStatus === 'CallConnected' || 
                   data.telephonyStatus === 'OnHold') {
            newStatus = 'OnCall';
        }
        // Check for DND status (before user status)
        else if (data.dndStatus === 'DoNotAcceptAnyCalls' || 
                 data.dndStatus === 'DoNotAcceptDepartmentCalls') {
            newStatus = 'DND';
        }
        // Check for user status
        else if (data.userStatus) {
            newStatus = data.userStatus;
        } else if (data.presenceStatus) {
            newStatus = data.presenceStatus;
        }
        // Check for telephony status when no call
        else if (data.telephonyStatus === 'NoCall') {
            // Use userStatus if available, otherwise Available
            newStatus = data.userStatus || data.presenceStatus || 'Available';
        }
        
        // Normalize status names
        if (newStatus === 'Available' || newStatus === 'available') {
            newStatus = 'Available';
        } else if (newStatus === 'Busy' || newStatus === 'busy') {
            newStatus = 'Busy';
        } else if (newStatus === 'DoNotDisturb' || newStatus === 'DND' || newStatus === 'dnd') {
            newStatus = 'DND';
        }
        
        if (this.state.userStatus !== newStatus) {
            this.state.userStatus = newStatus;
        }
    }

    _checkWidgetVisibility() {
        const widget = document.getElementById("rc-widget");
        if (widget) {
            const isVisible = widget.classList.contains('rc-widget-visible') ||
                            (window.getComputedStyle(widget).display !== 'none' &&
                             window.getComputedStyle(widget).visibility !== 'hidden' &&
                             window.getComputedStyle(widget).opacity !== '0');
            if (this.state.widgetVisible !== isVisible) {
                this.state.widgetVisible = isVisible;
            }
            
            // Request status and authentication update from widget if visible
            if (isVisible) {
                this._requestStatusFromWidget();
            }
        } else {
            if (this.state.widgetVisible !== false) {
                this.state.widgetVisible = false;
            }
            // Widget doesn't exist, user is not logged in
            this.state.isLoggedIn = false;
        }
    }

    _requestStatusFromWidget() {
        // Request presence/status from widget
        const widget = document.getElementById("rc-widget");
        if (!widget) return;
        
        const iframe = widget.querySelector("iframe");
        const adapterFrame = document.querySelector("#rc-widget-adapter-frame");
        
        const targets = [
            iframe && iframe.contentWindow,
            adapterFrame && adapterFrame.contentWindow,
            window
        ].filter(Boolean);
        
        for (const target of targets) {
            if (target) {
                // Request authentication status
                target.postMessage({ type: "rc-adapter-get-state" }, "*");
                // Request presence update
                target.postMessage({ type: "rc-adapter-get-presence" }, "*");
                target.postMessage({ type: "rc-adapter-get-status" }, "*");
                // Also try to get current state
                target.postMessage({ type: "rc-adapter-request-presence" }, "*");
            }
        }
    }

    onClick(ev) {
        if (ev) {
            ev.preventDefault();
            ev.stopPropagation();
        }
        try {
            // Ensure adapter is loaded
            if (!document.querySelector('script[src*="ringcentral-embeddable"]')) {
                this.state.loading = true;
                const script = document.createElement("script");
                script.src = "https://apps.ringcentral.com/integration/ringcentral-embeddable/latest/adapter.js";
                script.async = true;
                script.onload = () => {
                    this.state.loading = false;
                    window.ringcentralAdapterReady = true;
                    setTimeout(() => this.toggleWidget(), 500);
                };
                document.head.appendChild(script);
            } else {
                this.toggleWidget();
            }
        } catch (e) {
            this.state.loading = false;
            console.error("Error loading RingCentral widget:", e);
        }
    }

    toggleWidget() {
        // Mark that we're toggling (so we don't block our own minimize messages)
        this._isToggling = true;
        
        // Check actual widget state, not internal state
        const widget = document.getElementById("rc-widget");
        if (!widget) {
            // Widget doesn't exist yet, show it
            showRingCentralWidget();
            this._isToggling = false;
            return;
        }

        // Check if widget is currently visible
        const isCurrentlyVisible = widget.classList.contains('rc-widget-visible') ||
                                  (window.getComputedStyle(widget).display !== 'none' &&
                                   window.getComputedStyle(widget).visibility !== 'hidden' &&
                                   window.getComputedStyle(widget).opacity !== '0');

        // Toggle based on actual state
        const shouldShow = !isCurrentlyVisible;

        try {
            const iframe = widget.querySelector("iframe");
            const targets = [iframe && iframe.contentWindow, window].filter(Boolean);

            if (shouldShow) {
                // Show widget
                widget.style.cssText = "display: block !important; visibility: visible !important; opacity: 1 !important; position: fixed !important; bottom: 20px !important; right: 20px !important; z-index: 1000 !important; max-width: 400px !important; max-height: 600px !important; pointer-events: auto !important;";
                widget.classList.add("rc-widget-visible");
                this.state.widgetVisible = true;
                
                // Tell adapter to show
                for (const target of targets) {
                    if (target) {
                        target.postMessage({ type: "rc-adapter-set-minimized", minimized: false }, "*");
                        target.postMessage({ type: "rc-adapter-open-dialer" }, "*");
                    }
                }
            } else {
                // Hide widget
                widget.style.cssText = "display: none !important; visibility: hidden !important; opacity: 0 !important; pointer-events: none !important;";
                widget.classList.remove("rc-widget-visible");
                this.state.widgetVisible = false;
                
                // Tell adapter to minimize
                for (const target of targets) {
                    if (target) {
                        target.postMessage({ type: "rc-adapter-set-minimized", minimized: true }, "*");
                    }
                }
            }
        } catch (e) {
            console.error("Error toggling widget:", e);
        } finally {
            // Reset toggle flag after a short delay
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
        // Toggle dropdown
        this.state.showStatusDropdown = !this.state.showStatusDropdown;
    }

    setStatus(ev) {
        if (ev) {
            ev.preventDefault();
            ev.stopPropagation();
        }
        
        // Don't allow status change if not logged in
        if (!this.state.isLoggedIn) {
            // Close dropdown
            this.state.showStatusDropdown = false;
            return;
        }
        
        const status = ev.currentTarget.getAttribute('data-status');
        const dndStatus = ev.currentTarget.getAttribute('data-dnd');
        
        // Send status to widget
        const widget = document.getElementById("rc-widget");
        if (widget) {
            const iframe = widget.querySelector("iframe");
            const adapterFrame = document.querySelector("#rc-widget-adapter-frame");
            
            const targets = [
                iframe && iframe.contentWindow,
                adapterFrame && adapterFrame.contentWindow,
                window
            ].filter(Boolean);
            
            for (const target of targets) {
                if (target) {
                    target.postMessage({
                        type: 'rc-adapter-set-presence',
                        userStatus: status,
                        dndStatus: dndStatus,
                    }, '*');
                }
            }
            
            // Ensure widget stays visible after status change
            this._ensureWidgetStaysVisible();
        }
        
        // Update local state
        if (dndStatus === 'DoNotAcceptAnyCalls' || dndStatus === 'DoNotAcceptDepartmentCalls') {
            this.state.userStatus = 'DND';
        } else {
            this.state.userStatus = status;
        }
        
        // Close dropdown
        this.state.showStatusDropdown = false;
    }


    // Cleanup on unmount
    willUnmount() {
        if (this._visibilityCheckInterval) {
            clearInterval(this._visibilityCheckInterval);
        }
        if (this._messageListener) {
            window.removeEventListener('message', this._messageListener);
        }
    }
    
    get iconPath() {
        // Return icon path based on widget visibility
        // Use Odoo's asset path format
        const baseUrl = window.location.origin;
        if (this.state.widgetVisible) {
            return `${baseUrl}/ringcentral_integration/static/src/img/rc_icon_visible.png`;
        } else {
            return `${baseUrl}/ringcentral_integration/static/src/img/rc_icon_hidden.svg`;
        }
    }

    get statusColor() {
        // Return color based on user status
        const statusColors = {
            'Available': '#28a745',      // Green
            'Busy': '#dc3545',            // Red
            'OnCall': '#ff9800',          // Orange
            'Ringing': '#ffc107',         // Yellow/Amber
            'DND': '#6c757d',             // Gray
            'Offline': '#adb5bd',        // Light gray
        };
        return statusColors[this.state.userStatus] || statusColors['Offline'];
    }

    get statusTitle() {
        // Return tooltip text based on status
        return `RingCentral - ${this.state.userStatus}`;
    }

    get statusIconClass() {
        // Return icon class based on status - use fa-circle for most, fa-ban for DND
        if (this.state.userStatus === 'DND') {
            return 'fa fa-ban';
        }
        return 'fa fa-circle';
    }

    get statusIconStyle() {
        // Return style string for status icon with status color
        const color = this.statusColor || '#adb5bd';
        return `color: ${color} !important; font-size: 14px !important; display: inline-block !important;`;
    }
}

// Export showRingCentralWidget for use in helper
window.showRingCentralWidget = showRingCentralWidget;

registry.category("systray").add("ringcentral_integration.RCPhoneSystray", {
    Component: RCPhoneSystray,
}, { sequence: 99 });
