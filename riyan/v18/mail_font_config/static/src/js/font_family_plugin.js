/** @odoo-module **/

import { Plugin } from "@html_editor/plugin";
import { _t } from "@web/core/l10n/translation";
import { reactive } from "@odoo/owl";
import { formatsSpecs } from "@html_editor/utils/formatting";
import { FontSelector } from "@html_editor/main/font/font_selector";
import { withSequence } from "@html_editor/utils/resource";
import { closestElement } from "@html_editor/utils/dom_traversal";
import { isBlock } from "@html_editor/utils/blocks";
import { findNode, closestPath } from "@html_editor/utils/dom_traversal";

// ─── 1. Inject 'fontFamily' format into Odoo's engine ──────────────────────
// This is necessary because Odoo 18's FormatPlugin relies on formatsSpecs.
if (!formatsSpecs.fontFamily) {
    formatsSpecs.fontFamily = {
        isFormatted: (node, props) => {
            const font = props?.fontFamily;
            return !!findNode(
                closestPath(node),
                (el) => {
                    const style = el.style?.fontFamily;
                    if (!style) return false;
                    // Normalize quotes to single-quotes for comparison
                    const normalized = style.replace(/"/g, "'");
                    return font ? normalized.includes(font) : true;
                },
                isBlock
            );
        },
        hasStyle: (node) => node.style && node.style["font-family"],
        addStyle: (node, props) => {
            node.style["font-family"] = props.fontFamily;
        },
        removeStyle: (node) => {
            node.style.removeProperty("font-family");
            if (node.getAttribute("style") === "") {
                node.removeAttribute("style");
            }
        },
    };
}

export const fontFamilyItems = [
    { name: "Arial", fontFamily: "Arial, Helvetica, sans-serif" },
    { name: "Verdana", fontFamily: "Verdana, Geneva, sans-serif" },
    { name: "Courier New", fontFamily: "'Courier New', Courier, monospace" },
    { name: "Georgia", fontFamily: "Georgia, serif" },
    { name: "Times New Roman", fontFamily: "'Times New Roman', Times, serif" },
    { name: "Tahoma", fontFamily: "Tahoma, Geneva, sans-serif" },
    { name: "Lucida Console", fontFamily: "'Lucida Console', Monaco, monospace" },
];

export class FontFamilyPlugin extends Plugin {
    static id = "fontFamily";
    static dependencies = ["selection", "format", "dom"];

    resources = {
        toolbar_groups: [
            // Ensure it appears near the font (Heading) selector
            withSequence(11, { id: "font-family" }),
        ],
        toolbar_items: [
            {
                id: "fontFamily",
                groupId: "font-family",
                title: _t("Font Family"),
                Component: FontSelector,
                props: {
                    getItems: () => fontFamilyItems,
                    getDisplay: () => this.fontFamily,
                    onSelected: (item) => {
                        this.dependencies.format.formatSelection("fontFamily", {
                            formatProps: { fontFamily: item.fontFamily },
                            applyStyle: true,
                        });
                        this.updateFontFamilyDisplay();
                    },
                },
            },
        ],
        selectionchange_handlers: [
            this.updateFontFamilyDisplay.bind(this),
        ],
    };

    setup() {
        this.fontFamily = reactive({ displayName: "Arial" });
    }

    get currentFontFamilyName() {
        const sel = this.dependencies.selection.getSelectionData().deepEditableSelection;
        if (!sel) return "Arial";

        const anchorNode = sel.anchorNode;
        const el = closestElement(anchorNode);
        if (!el) return "Arial";

        // Walk up to find the closest font-family
        let current = el;
        while (current && !isBlock(current)) {
            const style = current.style?.fontFamily;
            if (style) {
                const normalized = style.replace(/"/g, "'");
                const found = fontFamilyItems.find(item => normalized.includes(item.name) || item.fontFamily === normalized);
                if (found) return found.name;
            }
            current = current.parentElement;
        }
        return "Arial";
    }

    updateFontFamilyDisplay() {
        this.fontFamily.displayName = this.currentFontFamilyName;
    }
}
