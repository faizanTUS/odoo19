/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Popover } from "@web/core/popover/popover";

/**
 * Odoo 19.1+ registers pointerdown listeners on every iframe inside
 * Popover's useClickAway hook. Cross-origin iframes (e.g. RingCentral
 * embeddable) throw SecurityError when addEventListener is accessed.
 *
 * Temporarily detach those iframes while Popover.setup runs so the core
 * hook does not touch them. Mirrors odoo/odoo#272872.
 */
function isCrossOriginIframe(iframe) {
    try {
        void iframe.contentWindow.addEventListener;
        return false;
    } catch (error) {
        return error.name === "SecurityError";
    }
}

function withCrossOriginIframesDetached(callback) {
    const detached = [];
    for (const iframe of document.querySelectorAll("iframe")) {
        if (!isCrossOriginIframe(iframe)) {
            continue;
        }
        detached.push({
            iframe,
            parent: iframe.parentNode,
            next: iframe.nextSibling,
        });
        iframe.parentNode.removeChild(iframe);
    }
    try {
        return callback();
    } finally {
        for (const { iframe, parent, next } of detached) {
            if (next) {
                parent.insertBefore(iframe, next);
            } else {
                parent.appendChild(iframe);
            }
        }
    }
}

patch(Popover.prototype, {
    setup() {
        return withCrossOriginIframesDetached(() => super.setup());
    },
});
