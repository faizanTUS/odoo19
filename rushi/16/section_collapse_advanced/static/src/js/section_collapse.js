/** @odoo-module **/

console.warn(">>> SECTION COLLAPSE JS LOADED (DOM observer mode) <<<");

/**
 * Wait until document.body exists (Odoo loads modules before <body>).
 */
function waitForBody() {
    return new Promise((resolve) => {
        if (document.body) {
            resolve(document.body);
            return;
        }
        const interval = setInterval(() => {
            if (document.body) {
                clearInterval(interval);
                resolve(document.body);
            }
        }, 10);
    });
}

function buildSectionCollapse(root) {
    if (!root || root.nodeType !== 1) return;

    const tables = root.matches("table.o_list_table")
        ? [root]
        : [...root.querySelectorAll("table.o_list_table")];

    for (const table of tables) {
        const tbody = table.querySelector("tbody");
        if (!tbody) continue;

        const rows = [...tbody.querySelectorAll("tr.o_data_row")];
        if (!rows.length) continue;

        const hasSection = rows.some((r) =>
            r.classList.contains("o_is_line_section")
        );
        if (!hasSection) continue;

        const sections = [];
        let current = null;

        for (const row of rows) {
            const isSection = row.classList.contains("o_is_line_section");
            const isNote = row.classList.contains("o_is_line_note");

            if (isSection) {
                const id = row.dataset.id || `sc_${sections.length}`;
                current = { id, row, rows: [], count: 0 };
                sections.push(current);
                continue;
            }

            if (!current) continue;

            current.rows.push(row);
            if (!isNote) {
                current.count += 1;
            }
        }

        if (!sections.length) continue;

        for (const s of sections) {
            const collapsed = s.row.dataset.scCollapsed === "1";

            // hide/show lines of this section
            for (const r of s.rows) {
                r.style.display = collapsed ? "none" : "";
            }

            const cells = s.row.querySelectorAll("td");
            if (!cells.length) continue;

            // section label cell (second td in your markup)
            const target = cells.length >= 2 ? cells[1] : cells[0];

            let toggle = target.querySelector(".sc_section_toggle");
            if (!toggle) {
                toggle = document.createElement("span");
                toggle.className = "sc_section_toggle ms-2 o_clickable text-muted";
                toggle.onclick = () => {
                    const now = s.row.dataset.scCollapsed === "1";
                    s.row.dataset.scCollapsed = now ? "0" : "1";
                    buildSectionCollapse(table);   // local rebuild only
                };
                target.appendChild(toggle);
            }

            toggle.textContent =
                `${s.count} item${s.count === 1 ? "" : "s"} - ` +
                (collapsed ? "Expand" : "Collapse");
        }
    }
}

// ----------- RUN AFTER BODY EXISTS -----------
waitForBody().then((body) => {
    // initial pass
    buildSectionCollapse(body);


    let scheduled = false;
    const scheduleRebuild = () => {
        if (scheduled) return;
        scheduled = true;
        requestAnimationFrame(() => {
            scheduled = false;
            buildSectionCollapse(body);
        });
    };

    const observer = new MutationObserver((mutations) => {
        for (const m of mutations) {
            if (m.type === "childList") {
                scheduleRebuild();
                break;
            }
        }
    });

    observer.observe(body, {
        childList: true,
        subtree: true,   // but NOT attributes
    });
});
