/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Chatter } from "@mail/chatter/web_portal/chatter";
import { Thread } from "@mail/core/common/thread";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { useService } from "@web/core/utils/hooks";
import { DateTimeInput } from "@web/core/datetime/datetime_input";

/**
 * Advanced Chatter Filter Module
 * 
 * Provides high-quality, reactive filtering for Odoo 19 chatter.
 * Supports filtering by message type (Communication, Sent, Received, Notes, System, Activities)
 * and by date (Today, Yesterday, Custom Range).
 */

// Global registration of UI components used in the custom chatter templates
Object.assign(Chatter.components, { Dropdown, DropdownItem, DateTimeInput });

// Register custom props for Thread component to ensure reactivity across patches
const threadProps = ["chatterFilter?", "dateFilter?", "startDate?", "endDate?"];
threadProps.forEach(prop => {
    if (!Thread.props.includes(prop)) {
        Thread.props.push(prop);
    }
});

// ── Chatter Component Patch ──────────────────────────────────────────────────
// Manages the state of the filter UI and provides data to the message list.
patch(Chatter.prototype, {
    /**
     * @override
     * Initialize filter states for type and date selection.
     */
    setup() {
        super.setup();
        this.state.chatterFilter = "all";
        this.state.dateFilter = "all";
        this.state.startDate = null;
        this.state.endDate = null;
    },

    /**
     * Getter for current chatter filter (reactive to state).
     */
    get chatterFilter() {
        return this.state.chatterFilter ?? "all";
    },

    /**
     * Update the active chatter category and trigger re-render.
     * @param {string} val - Category key (e.g., 'communication', 'sent').
     */
    setChatterFilter(val) {
        this.state.chatterFilter = val;
    },

    /**
     * Getter for current date filter (reactive to state).
     */
    get dateFilter() {
        return this.state.dateFilter ?? "all";
    },

    /**
     * Update active date filter and clear custom dates if a preset is selected.
     * @param {string} val - Date filter key ('all', 'today', 'yesterday', 'custom').
     */
    setDateFilter(val) {
        this.state.dateFilter = val;
        if (val !== "custom") {
            this.state.startDate = null;
            this.state.endDate = null;
        }
    },

    /**
     * Handler for custom start date changes.
     */
    onStartDateChange(val) {
        this.state.startDate = val;
        this.state.dateFilter = "custom";
    },

    /**
     * Handler for custom end date changes.
     */
    onEndDateChange(val) {
        this.state.endDate = val;
        this.state.dateFilter = "custom";
    },

    /**
     * Reactive getter for planned activities.
     * Overrides base activities to support date-based filtering.
     * Checks both 'create_date' and 'date_deadline' against selected filters.
     */
    get activities() {
        if (!this.state.thread) return [];
        const activities = this.state.thread.activities;
        const { dateFilter, startDate, endDate } = this.state;
        
        // Show all if no date filter is active
        if (dateFilter === "all" || !dateFilter) {
            return activities;
        }
        
        const today = luxon.DateTime.now().startOf("day");
        return activities.filter((a) => {
            if (!a.create_date || !a.date_deadline) return true;
            const createDate = a.create_date.startOf("day");
            const deadlineDate = a.date_deadline.startOf("day");
            
            if (dateFilter === "today") {
                return createDate.equals(today) || deadlineDate.equals(today);
            } else if (dateFilter === "yesterday") {
                const yesterday = today.minus({ days: 1 });
                return createDate.equals(yesterday) || deadlineDate.equals(yesterday);
            } else if (dateFilter === "custom" && startDate) {
                const start = startDate.startOf("day");
                if (endDate) {
                    const end = endDate.startOf("day");
                    return (createDate >= start && createDate <= end) || 
                           (deadlineDate >= start && deadlineDate <= end);
                }
                // Single date match if end date is missing
                return createDate.equals(start) || deadlineDate.equals(start);
            }
            return false;
        });
    },
});

// ── Thread Component Patch ───────────────────────────────────────────────────
// Core filtering logic for the message sequence list.
patch(Thread.prototype, {
    /**
     * @override
     * Cascading filter for both type (Category) and date.
     * Priority given to strictly separating Communication from internal Notes.
     */
    get orderedMessages() {
        const messages = this.state.mountedAndLoaded
            ? this.props.thread.messages
            : this.props.thread.phantomMessages;

        const chatterFilter = this.props.chatterFilter ?? "all";
        const dateFilter = this.props.dateFilter ?? "all";

        let filtered = [...messages];

        // 1. PHASE 1: Category Filtering (Type)
        if (chatterFilter !== "all") {
            switch (chatterFilter) {
                case "communication":
                    // Strictly exclude internal notes and system tracking
                    filtered = filtered.filter((m) =>
                        (m.message_type === "email" || m.isDiscussion) &&
                        !m.isNote &&
                        m.message_type !== "notification" &&
                        m.message_type !== "user_notification" &&
                        !m.trackingValues?.length
                    );
                    break;
                case "sent":
                    filtered = filtered.filter((m) =>
                        (m.message_type === "comment" || m.message_type === "email") &&
                        !m.isNote &&
                        (m.isSelfAuthored || (m.author?.main_user_id && m.author.main_user_id.share === false))
                    );
                    break;
                case "received":
                    filtered = filtered.filter((m) =>
                        (m.message_type === "comment" || m.message_type === "email") &&
                        !m.isNote &&
                        !m.isSelfAuthored &&
                        !(m.author?.main_user_id && m.author.main_user_id.share === false)
                    );
                    break;
                case "system":
                    filtered = filtered.filter(
                        (m) => m.message_type === "notification" ||
                            m.message_type === "auto_comment" ||
                            m.message_type === "user_notification"
                    );
                    break;
                case "notes":
                    filtered = filtered.filter((m) => m.isNote && m.message_type === "comment");
                    break;
                case "activities":
                    filtered = [];
                    break;
            }
        }

        // 2. PHASE 2: Date Filtering
        if (dateFilter !== "all") {
            const today = luxon.DateTime.now().startOf("day");
            filtered = filtered.filter((m) => {
                if (!m.datetime) return false;
                const msgDate = m.datetime.startOf("day");
                
                if (dateFilter === "today") {
                    return msgDate.equals(today);
                } else if (dateFilter === "yesterday") {
                    return msgDate.equals(today.minus({ days: 1 }));
                } else if (dateFilter === "custom" && this.props.startDate) {
                    const start = this.props.startDate.startOf("day");
                    if (this.props.endDate) {
                        const end = this.props.endDate.startOf("day");
                        return msgDate >= start && msgDate <= end;
                    }
                    // Handle single date match
                    return msgDate.equals(start);
                }
                return true;
            });
        }

        return this.props.order === "asc" ? filtered : filtered.reverse();
    },
});
