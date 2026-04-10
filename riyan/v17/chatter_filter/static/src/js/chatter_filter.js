/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Chatter } from "@mail/core/web/chatter";
import { Thread } from "@mail/core/common/thread";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { DateTimeInput } from "@web/core/datetime/datetime_input";
import { deserializeDate, deserializeDateTime } from "@web/core/l10n/dates";

Object.assign(Chatter.components, { Dropdown, DropdownItem, DateTimeInput });

const threadProps = ["chatterFilter?", "dateFilter?", "startDate?", "endDate?"];
threadProps.forEach((prop) => {
    if (!Thread.props.includes(prop)) {
        Thread.props.push(prop);
    }
});

patch(Chatter.prototype, {
    setup() {
        super.setup();
        this.state.chatterFilter = this.state.chatterFilter || "all";
        this.state.dateFilter = this.state.dateFilter || "all";
        this.state.startDate = this.state.startDate || null;
        this.state.endDate = this.state.endDate || null;
    },

    get chatterFilter() {
        return this.state.chatterFilter ?? "all";
    },

    setChatterFilter(val) {
        this.state.chatterFilter = val;
    },

    get dateFilter() {
        return this.state.dateFilter ?? "all";
    },

    setDateFilter(val) {
        this.state.dateFilter = val;
        if (val !== "custom") {
            this.state.startDate = null;
            this.state.endDate = null;
        }
    },

    onStartDateChange(val) {
        this.state.startDate = val;
        this.state.dateFilter = "custom";
    },

    onEndDateChange(val) {
        this.state.endDate = val;
        this.state.dateFilter = "custom";
    },

    get activities() {
        if (!this.state.thread) {
            return [];
        }
        const activities = this.state.thread.activities;
        const { dateFilter, startDate, endDate } = this.state;

        if (dateFilter === "all" || !dateFilter) {
            return activities;
        }

        const today = luxon.DateTime.now().startOf("day");
        const parseDate = (value, isDateTime = false) => {
            if (!value) {
                return null;
            }
            if (value?.isValid && typeof value.startOf === "function") {
                return value.startOf("day");
            }
            try {
                const dateValue = isDateTime ? deserializeDateTime(value) : deserializeDate(value);
                return dateValue?.startOf?.("day") || null;
            } catch {
                return null;
            }
        };

        return activities.filter((a) => {
            const createDate = parseDate(a.create_date, true);
            const deadlineDate = parseDate(a.date_deadline);
            const activityDates = [createDate, deadlineDate].filter(Boolean);
            if (!activityDates.length) {
                return true;
            }

            if (dateFilter === "today") {
                return activityDates.some((date) => date.equals(today));
            }
            if (dateFilter === "yesterday") {
                const yesterday = today.minus({ days: 1 });
                return activityDates.some((date) => date.equals(yesterday));
            }
            if (dateFilter === "custom" && startDate) {
                const start = startDate.startOf("day");
                if (endDate) {
                    const end = endDate.startOf("day");
                    return activityDates.some((date) => date >= start && date <= end);
                }
                return activityDates.some((date) => date.equals(start));
            }
            return false;
        });
    },
});

patch(Thread.prototype, {
    get filteredMessages() {
        const messages = this.props.thread?.nonEmptyMessages || [];
        const chatterFilter = this.props.chatterFilter ?? "all";
        const dateFilter = this.props.dateFilter ?? "all";

        let filtered = [...messages];

        if (chatterFilter !== "all") {
            switch (chatterFilter) {
                case "communication":
                    filtered = filtered.filter((m) =>
                        (m.type === "email" || m.type === "comment" || m.is_discussion) &&
                        !m.is_note &&
                        m.type !== "notification" &&
                        m.type !== "user_notification" &&
                        !m.trackingValues?.length
                    );
                    break;
                case "sent":
                    filtered = filtered.filter((m) =>
                        (m.type === "comment" || m.type === "email") &&
                        !m.is_note &&
                        m.isSelfAuthored
                    );
                    break;
                case "received":
                    filtered = filtered.filter((m) =>
                        (m.type === "comment" || m.type === "email") &&
                        !m.is_note &&
                        !m.isSelfAuthored
                    );
                    break;
                case "system":
                    filtered = filtered.filter(
                        (m) =>
                            m.type === "notification" ||
                            m.type === "auto_comment" ||
                            m.type === "user_notification" ||
                            Boolean(m.trackingValues?.length)
                    );
                    break;
                case "notes":
                    filtered = filtered.filter((m) => m.is_note && m.type === "comment");
                    break;
                case "activities":
                    filtered = [];
                    break;
            }
        }

        if (dateFilter !== "all") {
            const today = luxon.DateTime.now().startOf("day");
            filtered = filtered.filter((m) => {
                if (!m.datetime) {
                    return false;
                }
                const msgDate = m.datetime.startOf("day");

                if (dateFilter === "today") {
                    return msgDate.equals(today);
                }
                if (dateFilter === "yesterday") {
                    return msgDate.equals(today.minus({ days: 1 }));
                }
                if (dateFilter === "custom" && this.props.startDate) {
                    const start = this.props.startDate.startOf("day");
                    if (this.props.endDate) {
                        const end = this.props.endDate.startOf("day");
                        return msgDate >= start && msgDate <= end;
                    }
                    return msgDate.equals(start);
                }
                return true;
            });
        }

        return filtered;
    },
});
