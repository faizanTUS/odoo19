/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { SelectMenu } from "@web/core/select_menu/select_menu";
import { formatDelta } from "./dashboard_utils";

export class RcFilterSelect extends Component {
    static template = "ringcentral_integration.RcFilterSelect";
    static components = { SelectMenu };
    static props = {
        icon: String,
        value: { optional: true },
        choices: Array,
        placeholder: { type: String, optional: true },
        disabled: { type: Boolean, optional: true },
        searchable: { type: Boolean, optional: true },
        searchPlaceholder: { type: String, optional: true },
        autoSort: { type: Boolean, optional: true },
        onSelect: Function,
    };
    static defaultProps = {
        placeholder: "Select…",
        disabled: false,
        searchable: false,
        searchPlaceholder: "",
        autoSort: false,
    };

    setup() {
        this.uiState = useState({ isOpen: false });
    }

    /** SelectMenu shows placeholder when !value — avoid duplicate label in toggler. */
    get selectMenuPlaceholder() {
        return "";
    }

    get selectedLabel() {
        const choices = this.props.choices || [];
        const match = choices.find((c) => String(c.value) === String(this.props.value));
        if (match) {
            return match.label;
        }
        if (this.props.value) {
            return String(this.props.value);
        }
        return this.props.placeholder;
    }

    isSelected(choice) {
        return String(choice.value) === String(this.props.value);
    }

    onSelect(value) {
        this.props.onSelect(value === null || value === undefined ? "" : value);
    }

    onOpened() {
        this.uiState.isOpen = true;
    }

    onClosed() {
        this.uiState.isOpen = false;
    }
}

export class RcEmptyState extends Component {
    static template = "ringcentral_integration.RcEmptyState";
    static props = {
        message: { type: String, optional: true },
    };
}

export class RcLoading extends Component {
    static template = "ringcentral_integration.RcLoading";
    static props = {
        message: { type: String, optional: true },
    };
}

export class RcKpiCard extends Component {
    static template = "ringcentral_integration.RcKpiCard";
    static props = {
        kpi: Object,
        onClick: { type: Function, optional: true },
    };

    get deltaInfo() {
        const delta = this.props.kpi?.delta;
        if (delta === undefined || delta === null) {
            return null;
        }
        return formatDelta(delta);
    }

    onCardClick() {
        if (this.props.onClick) {
            this.props.onClick(this.props.kpi);
        }
    }
}

export class RcChartPanel extends Component {
    static template = "ringcentral_integration.RcChartPanel";
    static components = { RcEmptyState };
    static props = {
        title: String,
        subtitle: { type: String, optional: true },
        icon: { type: String, optional: true },
        empty: { type: Boolean, optional: true },
        emptyMessage: { type: String, optional: true },
        slots: { type: Object, optional: true },
    };

    get emptyMessageText() {
        return this.props.emptyMessage || "No data for the selected period.";
    }
}

export class RcLeaderboard extends Component {
    static template = "ringcentral_integration.RcLeaderboard";
    static components = { RcEmptyState };
    static props = {
        title: String,
        entries: { type: Array, optional: true },
        valueKey: { type: String, optional: true },
        onEntryClick: { type: Function, optional: true },
    };

    get items() {
        return this.props.entries || [];
    }

    onClickEntry(entry) {
        if (this.props.onEntryClick) {
            this.props.onEntryClick(entry);
        }
    }
}

export class RcAnalyticsCard extends Component {
    static template = "ringcentral_integration.RcAnalyticsCard";
    static props = {
        label: String,
        value: String,
        icon: { type: String, optional: true },
        accent: { type: String, optional: true },
        onClick: { type: Function, optional: true },
    };

    onCardClick() {
        if (this.props.onClick) {
            this.props.onClick();
        }
    }
}
