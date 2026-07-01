/** @odoo-module **/

/**
 * What we consider focusable / editable
 */
const FOCUSABLE_SELECTOR = "input, textarea, select, [contenteditable='true']";

function isInListView(target) {
    if (!target) return false;
    
    // Check for Odoo 19 list view structure - multiple selectors
    const listView = target.closest(".o_list_view");
    if (listView) return true;
    
    const listTable = target.closest("table.o_list_table");
    if (listTable) return true;
    
    // Check for table with data rows
    const table = target.closest("table");
    if (table) {
        // Check if it's inside a list view container
        const listContainer = table.closest(".o_list_view, .o_view_manager_content");
        if (listContainer) return true;
        
        // Check if table has list view structure
        if (table.querySelector(".o_data_row") || table.classList.contains("o_list_table")) {
            return true;
        }
    }
    
    return false;
}

function getCell(target) {
    if (!target) return null;
    // Odoo 19 uses .o_data_cell or td elements
    return target.closest("td.o_data_cell, td[data-name], td");
}

function getRow(cell) {
    if (!cell) return null;
    // Odoo 19 data rows
    return cell.closest("tr.o_data_row, tr[data-id], tbody tr");
}

function getTable(row) {
    if (!row) return null;
    return row.closest("table.o_list_table, table, .o_list_view table");
}

function isElementVisible(el) {
    if (!el) return false;
    const style = window.getComputedStyle(el);
    return style.visibility !== "hidden" && style.display !== "none" && style.opacity !== "0";
}

function getDataRows(table) {
    if (!table) {
        return [];
    }
    // Get all tbody rows, excluding header and footer
    const tbodyList = table.tBodies;
    const rows = [];
    for (const tbody of tbodyList) {
        for (const tr of tbody.rows) {
            // Exclude header, footer, and empty rows
            if (tr.classList.contains("o_list_footer") || 
                tr.classList.contains("o_list_header") ||
                tr.classList.contains("o_list_empty") ||
                tr.querySelector("th")) {
                continue;
            }
            // Only include rows that have data cells
            if (tr.querySelector("td")) {
                rows.push(tr);
            }
        }
    }
    return rows;
}

function getColumnIndex(row, cell) {
    if (!row || !cell) {
        return -1;
    }
    // Get all cells including th (for selector columns)
    const cells = Array.from(row.children);
    return cells.indexOf(cell);
}

function getFocusableInCell(cell) {
    if (!cell) {
        return null;
    }
    // First check if the cell itself is focusable
    if (cell.matches && cell.matches(FOCUSABLE_SELECTOR) && !cell.disabled && isElementVisible(cell)) {
        return cell;
    }
    // Search deeply inside cell for focusable elements
    // In Odoo 19, inputs might be in o_field_widget divs
    const candidates = cell.querySelectorAll(FOCUSABLE_SELECTOR);
    for (const el of candidates) {
        if (el.disabled || el.readOnly) continue;
        // Skip hidden inputs
        if (el.type === "hidden") continue;
        // In Odoo 19, inputs might not be visible until cell is in edit mode
        // So we check visibility more leniently - if it exists and isn't disabled, try it
        const style = window.getComputedStyle(el);
        // Only skip if explicitly hidden or display none
        if (style.display === "none" || style.visibility === "hidden") continue;
        return el;
    }
    return null;
}

function focusCellInRowByColumn(row, colIndex, placeCaretAtEnd = false) {
    if (!row || colIndex < 0) {
        return false;
    }
    const cells = Array.from(row.children);
    const targetCell = cells[colIndex];
    if (!targetCell) {
        return false;
    }
    
    // In Odoo 19, cells need to be clicked to enter edit mode
    // Try to find focusable element first
    let focusable = getFocusableInCell(targetCell);
    if (!focusable) {
        // Cell is not in edit mode, click it first to make it editable
        try {
            // Click the cell to enter edit mode
            const clickEvent = new MouseEvent('click', {
                bubbles: true,
                cancelable: true,
                view: window
            });
            targetCell.dispatchEvent(clickEvent);
            
            // Also try direct click
            if (targetCell.click) {
                targetCell.click();
            }
        } catch (e) {
            console.warn("Advanced List Navigation: Click error", e);
        }
        
        // Wait for Odoo to make the cell editable, then focus
        setTimeout(() => {
            focusable = getFocusableInCell(targetCell);
            if (focusable) {
                try {
                    focusable.focus();
                    if (focusable.setSelectionRange && typeof focusable.value === "string") {
                        const len = focusable.value.length;
                        const pos = placeCaretAtEnd ? len : 0;
                        try {
                            focusable.setSelectionRange(pos, pos);
                        } catch (_) {
                            // Some widgets might throw. ignore
                        }
                    }
                } catch (e) {
                    console.warn("Advanced List Navigation: Focus error", e);
                }
            } else {
                // Try one more time with a longer delay
                setTimeout(() => {
                    focusable = getFocusableInCell(targetCell);
                    if (focusable) {
                        try {
                            focusable.focus();
                            if (focusable.setSelectionRange && typeof focusable.value === "string") {
                                const len = focusable.value.length;
                                const pos = placeCaretAtEnd ? len : 0;
                                try {
                                    focusable.setSelectionRange(pos, pos);
                                } catch (_) {}
                            }
                        } catch (e) {
                            console.warn("Advanced List Navigation: Focus error (retry)", e);
                        }
                    }
                }, 100);
            }
        }, 100);
    } else {
        // Cell is already editable, just focus
        setTimeout(() => {
            try {
                focusable.focus();
                if (focusable.setSelectionRange && typeof focusable.value === "string") {
                    const len = focusable.value.length;
                    const pos = placeCaretAtEnd ? len : 0;
                    try {
                        focusable.setSelectionRange(pos, pos);
                    } catch (_) {
                        // Some widgets might throw. ignore
                    }
                }
            } catch (e) {
                console.warn("Advanced List Navigation: Focus error", e);
            }
        }, 10);
    }

    // Return true if we found a cell to work with (even if focus is async)
    return true;
}

function focusNextEditableInRow(row, currentCell, direction) {
    // direction: +1 => right, -1 => left
    if (!row || !currentCell) {
        return false;
    }

    const cells = Array.from(row.children);
    const currentIndex = cells.indexOf(currentCell);
    if (currentIndex === -1) {
        return false;
    }

    let index = currentIndex + direction;
    while (index >= 0 && index < cells.length) {
        const cell = cells[index];
        const focusable = getFocusableInCell(cell);
        if (focusable) {
            setTimeout(() => {
                try {
                    focusable.focus();
                    if (focusable.setSelectionRange && typeof focusable.value === "string") {
                        try {
                            if (direction > 0) {
                                focusable.setSelectionRange(0, 0);
                            } else {
                                const len = focusable.value.length;
                                focusable.setSelectionRange(len, len);
                            }
                        } catch (_) {}
                    }
                } catch (e) {
                    console.warn("Advanced List Navigation: Focus error", e);
                }
            }, 10);
            return true;
        }
        index += direction;
    }

    return false;
}

function moveVertical(input, key) {
    const cell = getCell(input);
    if (!cell) {
        return false;
    }
    
    const row = getRow(cell);
    if (!row) {
        return false;
    }
    
    const table = getTable(row);
    if (!table) {
        return false;
    }
    
    const colIndex = getColumnIndex(row, cell);
    const rows = getDataRows(table);
    if (colIndex < 0 || rows.length === 0) {
        return false;
    }

    const currentRowIndex = rows.indexOf(row);
    if (currentRowIndex === -1) {
        return false;
    }

    const direction = (key === "ArrowUp") ? -1 : 1;
    let index = currentRowIndex + direction;
    // Try to find next available cell in the same column
    while (index >= 0 && index < rows.length) {
        const targetRow = rows[index];
        const ok = focusCellInRowByColumn(targetRow, colIndex);
        if (ok) {
            return true;
        }
        index += direction;
    }
    return false;
}

function handleLeftRight(input, key) {
    // Only for input/textarea. others use pure cell nav
    const isInput = input instanceof HTMLInputElement;
    const isTextarea = input instanceof HTMLTextAreaElement;

    if (!isInput && !isTextarea) {
        const cell = getCell(input);
        const row = getRow(cell);
        const direction = key === "ArrowRight" ? 1 : -1;
        return focusNextEditableInRow(row, cell, direction);
    }

    const type = (input.type || "").toLowerCase();
    const isTextLike =
        isTextarea || !["checkbox", "radio", "button", "submit", "reset"].includes(type);

    const value = input.value || "";
    const length = value.length;

    if (!isTextLike || typeof input.selectionStart !== "number") {
        const cell = getCell(input);
        const row = getRow(cell);
        const direction = key === "ArrowRight" ? 1 : -1;
        return focusNextEditableInRow(row, cell, direction);
    }

    const start = input.selectionStart;
    const end = input.selectionEnd;
    const collapsed = start === end;

    if (!collapsed) {
        // User is selecting text. do not hijack
        return false;
    }

    const cell = getCell(input);
    const row = getRow(cell);

    if (key === "ArrowLeft" && start === 0) {
        return focusNextEditableInRow(row, cell, -1);
    }

    if (key === "ArrowRight" && start === length) {
        return focusNextEditableInRow(row, cell, 1);
    }

    // Otherwise normal caret behavior
    return false;
}

function handleTab(input, isShift) {
    const cell = getCell(input);
    const row = getRow(cell);
    const table = getTable(row);
    const rows = getDataRows(table);

    if (!row || !cell || rows.length === 0) {
        return false;
    }

    const cells = Array.from(row.children);
    const currentIndex = cells.indexOf(cell);
    if (currentIndex === -1) {
        return false;
    }

    const direction = isShift ? -1 : 1;

    // 1. Try in same row
    let index = currentIndex + direction;
    while (index >= 0 && index < cells.length) {
        const nextCell = cells[index];
        const focusable = getFocusableInCell(nextCell);
        if (focusable) {
            setTimeout(() => {
                try {
                    focusable.focus();
                    if (focusable.setSelectionRange && typeof focusable.value === "string") {
                        try {
                            if (!isShift) {
                                focusable.setSelectionRange(0, 0);
                            } else {
                                const len = focusable.value.length;
                                focusable.setSelectionRange(len, len);
                            }
                        } catch (_) {}
                    }
                } catch (e) {
                    console.warn("Advanced List Navigation: Focus error", e);
                }
            }, 10);
            return true;
        }
        index += direction;
    }

    // 2. Jump to another row
    const currentRowIndex = rows.indexOf(row);
    if (currentRowIndex === -1) {
        return false;
    }

    let nextRowIndex = currentRowIndex + direction;
    while (nextRowIndex >= 0 && nextRowIndex < rows.length) {
        const targetRow = rows[nextRowIndex];
        const targetCells = Array.from(targetRow.children);

        if (!targetCells.length) {
            nextRowIndex += direction;
            continue;
        }

        const orderedCells = isShift ? targetCells.slice().reverse() : targetCells;

        for (const c of orderedCells) {
            const focusable = getFocusableInCell(c);
            if (focusable) {
                setTimeout(() => {
                    try {
                        focusable.focus();
                        if (focusable.setSelectionRange && typeof focusable.value === "string") {
                            try {
                                if (!isShift) {
                                    focusable.setSelectionRange(0, 0);
                                } else {
                                    const len = focusable.value.length;
                                    focusable.setSelectionRange(len, len);
                                }
                            } catch (_) {}
                        }
                    } catch (e) {
                        console.warn("Advanced List Navigation: Focus error", e);
                    }
                }, 10);
                return true;
            }
        }

        nextRowIndex += direction;
    }

    return false;
}

// Wait for DOM to be ready
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

// Initialize the keyboard navigation
function initKeyboardNavigation() {
    // Use capture phase to ensure we catch events before other handlers
    function handleKeyDown(ev) {
        const key = ev.key;

        // Only handle arrow keys, Enter, and Tab
        if (!["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "Enter", "Tab"].includes(key)) {
            return;
        }

        const target = ev.target;
        // Only act on real editable elements
        if (!target || !target.matches || !target.matches(FOCUSABLE_SELECTOR)) {
            return;
        }

        // Check if we're in a list view
        const inListView = isInListView(target);
        if (!inListView) {
            return;
        }

        // For arrows and Enter, ignore Ctrl/Alt/Meta combos (but allow Shift for Tab)
        if (key !== "Tab" && (ev.ctrlKey || ev.metaKey || ev.altKey)) {
            return;
        }

        let handled = false;

        // Handle Up/Down arrows and Enter key
        if (key === "ArrowUp" || key === "ArrowDown" || key === "Enter") {
            // Enter behaves like ArrowDown
            const arrowKey = key === "Enter" ? "ArrowDown" : key;
            handled = moveVertical(target, arrowKey);
        } else if (key === "ArrowLeft" || key === "ArrowRight") {
            handled = handleLeftRight(target, key);
        } else if (key === "Tab") {
            handled = handleTab(target, ev.shiftKey);
        }

        if (handled) {
            ev.preventDefault();
            ev.stopPropagation();
            ev.stopImmediatePropagation();
        } else {
        }
    }

    // Attach event listener with capture phase
    document.addEventListener("keydown", handleKeyDown, true);
}

// Wait for body, then initialize
waitForBody().then(() => {
    // Wait a bit more for Odoo to be ready
    if (document.readyState === 'complete') {
        setTimeout(initKeyboardNavigation, 500);
    } else {
        window.addEventListener('load', () => {
            setTimeout(initKeyboardNavigation, 500);
        });
        // Also try immediately if DOM is already ready
        if (document.readyState === 'interactive' || document.readyState === 'complete') {
            setTimeout(initKeyboardNavigation, 500);
        }
    }
});
