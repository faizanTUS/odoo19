/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { attr } from '@mail/model/model_field';
import { clear } from '@mail/model/model_field_command';

const DATE_FORMAT = 'YYYY-MM-DD';

function parseDateInput(value) {
    if (!value) {
        return null;
    }
    const date = moment(value, DATE_FORMAT, true);
    return date.isValid() ? date.startOf('day') : null;
}

function parseActivityDate(value) {
    if (!value) {
        return null;
    }
    const date = moment(value);
    return date.isValid() ? date.startOf('day') : null;
}

function messageMatchesType(message, chatterFilter) {
    if (!chatterFilter || chatterFilter === 'all') {
        return true;
    }
    switch (chatterFilter) {
        case 'communication':
            return (
                (message.message_type === 'email' || message.message_type === 'comment' || message.is_discussion) &&
                !message.is_note &&
                message.message_type !== 'notification' &&
                message.message_type !== 'user_notification' &&
                message.trackingValues.length === 0
            );
        case 'sent':
            return (
                (message.message_type === 'comment' || message.message_type === 'email') &&
                !message.is_note &&
                message.isCurrentUserOrGuestAuthor
            );
        case 'received':
            return (
                (message.message_type === 'comment' || message.message_type === 'email') &&
                !message.is_note &&
                !message.isCurrentUserOrGuestAuthor
            );
        case 'notes':
            return message.is_note && message.message_type === 'comment';
        case 'system':
            return (
                message.message_type === 'notification' ||
                message.message_type === 'auto_comment' ||
                message.message_type === 'user_notification' ||
                message.trackingValues.length > 0
            );
        case 'activities':
            return false;
        default:
            return true;
    }
}

function dateMatches(filter, startDate, endDate, candidateDate) {
    if (!filter || filter === 'all') {
        return true;
    }
    if (!candidateDate || !candidateDate.isValid()) {
        return false;
    }
    const day = candidateDate.clone().startOf('day');
    const today = moment().startOf('day');
    if (filter === 'today') {
        return day.isSame(today, 'day');
    }
    if (filter === 'yesterday') {
        return day.isSame(today.clone().subtract(1, 'day'), 'day');
    }
    if (filter === 'custom') {
        const start = parseDateInput(startDate);
        const end = parseDateInput(endDate);
        if (start && end) {
            const from = start.isSameOrBefore(end, 'day') ? start : end;
            const to = start.isSameOrBefore(end, 'day') ? end : start;
            return day.isBetween(from, to, 'day', '[]');
        }
        if (start) {
            return day.isSame(start, 'day');
        }
        if (end) {
            return day.isSame(end, 'day');
        }
    }
    return true;
}

function messageMatchesDate(message, chatter) {
    return dateMatches(chatter.dateFilter, chatter.startDate, chatter.endDate, message.date);
}

function activityMatchesDate(activity, chatter) {
    if (!chatter || !chatter.dateFilter || chatter.dateFilter === 'all') {
        return true;
    }
    const createDate = parseActivityDate(activity.dateCreate);
    const deadlineDate = parseActivityDate(activity.dateDeadline);
    const candidates = [createDate, deadlineDate].filter(Boolean);
    if (candidates.length === 0) {
        return true;
    }
    return candidates.some((date) => dateMatches(chatter.dateFilter, chatter.startDate, chatter.endDate, date));
}

registerPatch({
    name: 'Chatter',
    recordMethods: {
        setChatterFilter(filter) {
            this.update({ chatterFilter: filter || 'all' });
        },
        setDateFilter(filter) {
            if (filter === 'custom') {
                this.update({ dateFilter: 'custom' });
                return;
            }
            this.update({
                dateFilter: filter || 'all',
                startDate: '',
                endDate: '',
            });
        },
        onClickChatterFilterItem(ev) {
            ev.preventDefault();
            this.setChatterFilter(ev.currentTarget.dataset.filter);
        },
        onClickDateFilterItem(ev) {
            ev.preventDefault();
            this.setDateFilter(ev.currentTarget.dataset.dateFilter);
        },
        onChangeFilterStartDate(ev) {
            const startDate = ev.target.value || '';
            this.update({
                startDate,
                dateFilter: startDate || this.endDate ? 'custom' : 'all',
            });
        },
        onChangeFilterEndDate(ev) {
            const endDate = ev.target.value || '';
            this.update({
                endDate,
                dateFilter: this.startDate || endDate ? 'custom' : 'all',
            });
        },
        onClickClearCustomDate(ev) {
            ev.preventDefault();
            this.update({
                dateFilter: 'all',
                startDate: '',
                endDate: '',
            });
        },
    },
    fields: {
        chatterFilter: attr({
            default: 'all',
        }),
        dateFilter: attr({
            default: 'all',
        }),
        startDate: attr({
            default: '',
        }),
        endDate: attr({
            default: '',
        }),
        filterLabel: attr({
            compute() {
                if (this.dateFilter === 'custom' && this.startDate) {
                    const start = parseDateInput(this.startDate);
                    const end = parseDateInput(this.endDate);
                    if (!start) {
                        return this.env._t('Custom Range');
                    }
                    if (end) {
                        return `${start.format('MMM D')} - ${end.format('MMM D')}`;
                    }
                    return start.format('MMM D');
                }
                const labels = {
                    all: this.env._t('All Messages'),
                    communication: this.env._t('Communication'),
                    sent: this.env._t('Sent'),
                    received: this.env._t('Received'),
                    notes: this.env._t('Notes'),
                    system: this.env._t('System'),
                    activities: this.env._t('Activities'),
                };
                return labels[this.chatterFilter || 'all'] || labels.all;
            },
        }),
        activityBoxView: {
            compute() {
                if (!this.thread || !this.thread.hasActivities || this.thread.activities.length === 0) {
                    return clear();
                }
                if (!['all', 'activities'].includes(this.chatterFilter || 'all')) {
                    return clear();
                }
                return {};
            },
        },
    },
});

registerPatch({
    name: 'ActivityBoxView',
    fields: {
        activityViews: {
            compute() {
                if (!this.chatter || !this.chatter.thread) {
                    return clear();
                }
                const chatter = this.chatter;
                const activities = chatter.thread.activities.filter((activity) =>
                    activityMatchesDate(activity, chatter)
                );
                return activities.map((activity) => ({ activity }));
            },
        },
    },
});

registerPatch({
    name: 'MessageListView',
    fields: {
        filteredOrderedMessages: attr({
            compute() {
                if (!this.threadViewOwner.threadCache) {
                    return clear();
                }
                const chatter = this.threadViewOwner.threadViewer && this.threadViewOwner.threadViewer.chatter;
                const messages = [...this.threadViewOwner.threadCache.orderedNonEmptyMessages].filter((message) => {
                    if (!chatter) {
                        return true;
                    }
                    return (
                        messageMatchesType(message, chatter.chatterFilter || 'all') &&
                        messageMatchesDate(message, chatter)
                    );
                });
                if (this.threadViewOwner.order === 'desc') {
                    messages.reverse();
                }
                return messages;
            },
        }),
        messageListViewItems: {
            compute() {
                if (!this.threadViewOwner.threadCache) {
                    return clear();
                }
                const messageViewsData = [];
                let prevMessage;
                for (const message of (this.filteredOrderedMessages || [])) {
                    messageViewsData.push({
                        isSquashed: this.threadViewOwner._shouldMessageBeSquashed(prevMessage, message),
                        message,
                    });
                    prevMessage = message;
                }
                return messageViewsData;
            },
        },
    },
});
