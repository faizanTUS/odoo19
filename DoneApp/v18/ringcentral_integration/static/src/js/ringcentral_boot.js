// Auto-load the RingCentral Embeddable adapter on webclient load.
// The adapter will create the floating widget (div#rc-widget) automatically.
// This script waits for Odoo to fully initialize before loading the adapter.
// NOTE: This is NOT an @odoo-module to avoid blocking Odoo's initialization.

(function() {
    'use strict';
    
    let adapterInitialized = false;
    let initStarted = false;

    async function fetchConfig() {
        try {
            // Use fetch API instead of rpc to avoid blocking Odoo module loading
            // Add timeout to prevent hanging requests
            const baseUrl = window.location.origin;
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
            
            try {
                // JSON-RPC 2.0 format for type='jsonrpc' endpoint (Odoo 19)
                const response = await fetch(`${baseUrl}/ringcentral/api/config`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',
                    signal: controller.signal,
                    body: JSON.stringify({
                        jsonrpc: '2.0',
                        method: 'call',
                        params: {},
                        id: Math.floor(Math.random() * 1000000),
                    }),
                });
                
                clearTimeout(timeoutId);
                
                if (response.ok) {
                    const result = await response.json();
                    // type='jsonrpc' returns JSON-RPC 2.0 format: {jsonrpc: "2.0", result: {...}, id: ...}
                    if (result.result) {
                        return result.result;
                    }
                    // Fallback: if result is not in JSON-RPC format, return as-is
                    return result;
                } else {
                    console.warn("RingCentral: Config request failed with status:", response.status);
                }
            } catch (fetchError) {
                clearTimeout(timeoutId);
                if (fetchError.name === 'AbortError') {
                    console.warn("RingCentral: Config request timed out");
                } else {
                    throw fetchError;
                }
            }
        } catch (error) {
            console.warn("RingCentral: Could not fetch config:", error);
        }
        return null;
    }

    async function ensureEmbeddableScript() {
        if (document.querySelector('script[src*="ringcentral-embeddable"]')) {
            return;
        }

        try {
            // Get optional configuration from backend (client_id, server_url)
            // Use fetch instead of rpc to avoid blocking
            let clientId = null;
            let server = 'prod';
            
            const config = await fetchConfig();
            if (config && config.data) {
                clientId = config.data.client_id;
                server = config.data.server_url === 'https://platform.ringcentral.com' ? 'prod' : 'dev';
            }

            const script = document.createElement("script");
            // Always load adapter; include params if available
            let adapterUrl = "https://apps.ringcentral.com/integration/ringcentral-embeddable/latest/adapter.js";
            if (clientId) {
                adapterUrl += `?clientId=${encodeURIComponent(clientId)}&appServer=${server}`;
            }

            script.src = adapterUrl;
            script.async = true;
            script.defer = true;
            script.onload = () => {
                adapterInitialized = true;
                window.ringcentralAdapterReady = true;
                hideWidgetRepeatedly();
            };
            document.head.appendChild(script);
        } catch (error) {
            console.warn("Failed to load RingCentral adapter:", error);
            // Fallback: load adapter without config
            const script = document.createElement("script");
            script.src = "https://apps.ringcentral.com/integration/ringcentral-embeddable/latest/adapter.js";
            script.async = true;
            script.defer = true;
            script.onload = () => {
                hideWidgetRepeatedly();
            };
            document.head.appendChild(script);
        }
    }

    function hideWidgetRepeatedly() {
        const hideWidget = () => {
            const widget = document.getElementById("rc-widget");
            if (widget && !widget.classList.contains('rc-widget-visible')) {
                // Only hide if not explicitly made visible
                widget.style.cssText = "display: none !important; visibility: hidden !important; opacity: 0 !important; position: fixed !important; bottom: 20px !important; right: 20px !important; z-index: 1000 !important; max-width: 400px !important; max-height: 600px !important; pointer-events: none !important;";
            }
        };
        
        // Check immediately
        hideWidget();
        
        // Check less frequently to reduce performance impact
        const checkInterval = setInterval(() => {
            hideWidget();
        }, 1000); // Reduced from 200ms to 1000ms (1 second)
        
        // Stop checking after 10 seconds (reduced from 15)
        setTimeout(() => clearInterval(checkInterval), 10000);
    }

    function waitForOdoo() {
        // Wait for Odoo web client to be ready
        // Check for Odoo's main app container
        const checkOdooReady = setInterval(() => {
            // Check if Odoo's main elements exist
            const odooMain = document.querySelector('.o_action_manager') || 
                            document.querySelector('.o_main_content') ||
                            document.querySelector('[data-oe-model]') ||
                            document.body.querySelector('.o_web_client');
            
            if (odooMain || document.body.children.length > 2) {
                clearInterval(checkOdooReady);
                // Wait a bit more to ensure Odoo is fully rendered
                setTimeout(() => {
                    if (!initStarted) {
                        initStarted = true;
                        ensureEmbeddableScript();
                    }
                }, 2000);
            }
        }, 500);
        
        // Stop checking after 30 seconds (Odoo should be loaded by then)
        setTimeout(() => {
            clearInterval(checkOdooReady);
            if (!initStarted) {
                initStarted = true;
                ensureEmbeddableScript();
            }
        }, 30000);
    }

    // Start waiting for Odoo after Odoo has had time to initialize
    // Use requestIdleCallback if available, otherwise setTimeout with longer delay
    if (window.requestIdleCallback) {
        requestIdleCallback(() => {
            setTimeout(waitForOdoo, 2000);
        }, { timeout: 5000 });
    } else {
        // Wait for window load event, then additional delay
        if (document.readyState === 'complete') {
            setTimeout(waitForOdoo, 3000);
        } else {
            window.addEventListener('load', () => {
                setTimeout(waitForOdoo, 3000);
            });
        }
    }
})();


