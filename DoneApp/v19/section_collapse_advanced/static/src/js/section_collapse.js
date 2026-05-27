/** @odoo-module **/

/**
 * Section Collapse Advanced
 * -------------------------
 * Adds an "N items - Expand / Collapse" toggle to every list-view section row
 * (rows that carry the `o_is_line_section` class). When toggled, all data rows
 * that belong to that section are hidden / shown until the next section row.
 *
 * Implementation notes:
 *   - Pure DOM-level enhancement, runs after the body exists.
 *   - A single MutationObserver watches list bodies; rebuilds are throttled
 *     through requestAnimationFrame and skipped when the only changes are
 *     produced by this module itself (style.display flips on data rows).
 *   - State is stored on `data-sc-collapsed` of the section row, so it survives
 *     in-place rerenders that preserve attributes.
 */

const SECTION_CLASS = "o_is_line_section";
const NOTE_CLASS = "o_is_line_note";
const TABLE_SELECTOR = "table.o_list_table";
const TOGGLE_CLASS = "sc_section_toggle";

function waitForBody() {
    return new Promise((resolve) => {
        if (document.body) {
            resolve(document.body);
            return;
        }
        const observer = new MutationObserver(() => {
            if (document.body) {
                observer.disconnect();
                resolve(document.body);
            }
        });
        observer.observe(document.documentElement, { childList: true });
    });
}

function getTables(root) {
    if (!root || root.nodeType !== 1) {
        return [];
    }
    if (root.matches && root.matches(TABLE_SELECTOR)) {
        return [root];
    }
    return Array.from(root.querySelectorAll(TABLE_SELECTOR));
}

function buildSectionsForTable(table) {
    const tbody = table.tBodies[0];
    if (!tbody) {
        return;
    }

    const rows = tbody.querySelectorAll("tr.o_data_row");
    if (!rows.length) {
        return;
    }

    const sections = [];
    let current = null;

    for (const row of rows) {
        const classList = row.classList;
        if (classList.contains(SECTION_CLASS)) {
            current = { row, rows: [], count: 0 };
            sections.push(current);
            continue;
        }
        if (!current) {
            continue;
        }
        current.rows.push(row);
        if (!classList.contains(NOTE_CLASS)) {
            current.count += 1;
        }
    }

    if (!sections.length) {
        return;
    }

    for (const section of sections) {
        applySectionState(section);
    }
}

function applySectionState(section) {
    const collapsed = section.row.dataset.scCollapsed === "1";
    const displayValue = collapsed ? "none" : "";

    for (const row of section.rows) {
        if (row.style.display !== displayValue) {
            row.style.display = displayValue;
        }
    }

    const cells = section.row.cells;
    if (!cells.length) {
        return;
    }
    const target = cells.length >= 2 ? cells[1] : cells[0];

    let toggle = target.querySelector(`.${TOGGLE_CLASS}`);
    if (!toggle) {
        toggle = document.createElement("span");
        toggle.className = `${TOGGLE_CLASS} ms-2 o_clickable text-muted`;
        toggle.addEventListener("click", (ev) => {
            ev.stopPropagation();
            const nowCollapsed = section.row.dataset.scCollapsed === "1";
            section.row.dataset.scCollapsed = nowCollapsed ? "0" : "1";
            applySectionState(section);
        });
        target.appendChild(toggle);
    }

    const itemLabel = section.count === 1 ? "item" : "items";
    toggle.textContent = `${section.count} ${itemLabel} - ${collapsed ? "Expand" : "Collapse"}`;
}

function buildSectionCollapse(root) {
    for (const table of getTables(root)) {
        buildSectionsForTable(table);
    }
}

function isOwnMutation(mutation) {
    if (mutation.type !== "attributes") {
        return false;
    }
    if (mutation.attributeName !== "style") {
        return false;
    }
    const target = mutation.target;
    return target && target.classList && target.classList.contains("o_data_row");
}

waitForBody().then((body) => {
    buildSectionCollapse(body);

    let scheduled = false;
    const scheduleRebuild = () => {
        if (scheduled) {
            return;
        }
        scheduled = true;
        requestAnimationFrame(() => {
            scheduled = false;
            buildSectionCollapse(body);
        });
    };

    const observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            if (mutation.type === "childList" && !isOwnMutation(mutation)) {
                scheduleRebuild();
                return;
            }
        }
    });

    observer.observe(body, {
        childList: true,
        subtree: true,
    });
});
