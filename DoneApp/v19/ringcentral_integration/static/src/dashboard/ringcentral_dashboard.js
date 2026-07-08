/** @odoo-module **/

import { Component, onMounted, onPatched, onWillStart, onWillUnmount, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets";
import { useService, useBus } from "@web/core/utils/hooks";
import { user, userBus } from "@web/core/user";
import {
    RcAnalyticsCard,
    RcChartPanel,
    RcFilterSelect,
    RcKpiCard,
    RcLeaderboard,
    RcLoading,
} from "./dashboard_components";
import {
    attachChartClick,
    barChartConfig,
    doughnutChartConfig,
    horizontalBarChartConfig,
    lineChartConfig,
} from "./dashboard_utils";

export class RingCentralDashboard extends Component {
    static template = "ringcentral_integration.RingCentralDashboard";
    static components = {
        RcKpiCard,
        RcChartPanel,
        RcLeaderboard,
        RcAnalyticsCard,
        RcLoading,
        RcFilterSelect,
    };
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this._loadDataPromise = null;
        this._debounceTimer = null;
        this._loadGeneration = 0;

        this.callTrendChartRef = useRef("callTrendChart");
        this.directionChartRef = useRef("directionChart");
        this.statusChartRef = useRef("statusChart");
        this.topUsersChartRef = useRef("topUsersChart");
        this.volumeChartRef = useRef("volumeChart");
        this.durationChartRef = useRef("durationChart");
        this.missedAnsweredChartRef = useRef("missedAnsweredChart");
        this.chartInstances = {};

        this.state = useState({
            loading: true,
            datePreset: "this_month",
            dateFrom: "",
            dateTo: "",
            userId: "",
            companyId: "",
            direction: "",
            status: "",
            granularity: "day",
            data: {
                kpis: [],
                charts: {},
                analytics: {},
                filter_options: {},
                period_label: "",
                is_admin: false,
            },
        });

        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
            await this.loadData();
        });
        onMounted(() => this.renderCharts());
        onPatched(() => this.renderCharts());
        useBus(userBus, "ACTIVE_COMPANIES_CHANGED", () => {
            if (user.activeCompany) {
                this.state.companyId = String(user.activeCompany.id);
            }
            this.state.userId = "";
            this.loadData();
        });
        onWillUnmount(() => {
            if (this._debounceTimer) {
                clearTimeout(this._debounceTimer);
            }
            Object.keys(this.chartInstances).forEach((key) => this._destroyChart(key));
        });
    }

    get isAdmin() {
        return this.state.data.is_admin;
    }

    get datePresets() {
        return this.state.data.filter_options?.date_presets || [
            { value: "this_month", label: "This Month" },
        ];
    }

    get datePresetChoices() {
        return this.datePresets;
    }

    get userChoices() {
        return [
            { value: "", label: "All users" },
            ...(this.filterUsers || []).map((user) => ({
                value: String(user.id),
                label: user.name,
            })),
        ];
    }

    get companyChoices() {
        return [
            { value: "", label: "All companies" },
            ...(this.filterCompanies || []).map((company) => ({
                value: String(company.id),
                label: company.name,
            })),
        ];
    }

    get directionChoices() {
        return [
            { value: "", label: "All directions" },
            ...(this.filterDirections || []).map((dir) => ({
                value: dir.value,
                label: dir.label,
            })),
        ];
    }

    get statusChoices() {
        return [
            { value: "", label: "All statuses" },
            ...(this.filterStatuses || []).map((st) => ({
                value: st.value,
                label: st.label,
            })),
        ];
    }

    get granularityChoices() {
        return [
            { value: "day", label: "By day" },
            { value: "week", label: "By week" },
            { value: "month", label: "By month" },
        ];
    }

    get filterUsers() {
        return this.state.data.filter_options?.users || [];
    }

    get filterCompanies() {
        return this.state.data.filter_options?.companies || [];
    }

    get filterDirections() {
        return this.state.data.filter_options?.directions || [];
    }

    get filterStatuses() {
        return this.state.data.filter_options?.statuses || [];
    }

    get isMultiCompany() {
        return this.state.data.filter_options?.is_multi_company;
    }

    get canFilterUsers() {
        return this.state.data.filter_options?.can_filter_users;
    }

    get showUserFilter() {
        return (this.filterUsers || []).length > 0;
    }

    get hasActiveFilters() {
        return this.activeFilterTags.length > 0;
    }

    get activeFilterTags() {
        const tags = [];
        const opts = this.state.data.filter_options || {};

        if (this.state.datePreset && this.state.datePreset !== "this_month") {
            const preset = (opts.date_presets || []).find((p) => p.value === this.state.datePreset);
            tags.push({
                key: "datePreset",
                label: preset?.label || this.state.datePreset,
                icon: "fa-calendar",
            });
        }
        if (this.state.datePreset === "custom" && this.state.dateFrom && this.state.dateTo) {
            tags.push({
                key: "customDate",
                label: `${this.state.dateFrom} → ${this.state.dateTo}`,
                icon: "fa-calendar-o",
            });
        }
        if (this.state.userId) {
            const user = this.filterUsers.find((u) => String(u.id) === String(this.state.userId));
            tags.push({
                key: "userId",
                label: user?.name || "User",
                icon: "fa-user",
            });
        }
        if (this.state.companyId) {
            const company = this.filterCompanies.find((c) => String(c.id) === String(this.state.companyId));
            tags.push({
                key: "companyId",
                label: company?.name || "Company",
                icon: "fa-building-o",
            });
        }
        if (this.state.direction) {
            const dir = this.filterDirections.find((d) => d.value === this.state.direction);
            tags.push({
                key: "direction",
                label: dir?.label || this.state.direction,
                icon: "fa-exchange",
            });
        }
        if (this.state.status) {
            const st = this.filterStatuses.find((s) => s.value === this.state.status);
            tags.push({
                key: "status",
                label: st?.label || this.state.status,
                icon: "fa-info-circle",
            });
        }
        if (this.state.granularity && this.state.granularity !== "day") {
            const granLabels = { week: "Week", month: "Month" };
            tags.push({
                key: "granularity",
                label: `Volume: ${granLabels[this.state.granularity] || this.state.granularity}`,
                icon: "fa-signal",
            });
        }
        return tags;
    }

    get analyticsSuccessRate() {
        const rate = this.state.data.analytics?.success_rate;
        return rate !== undefined ? `${rate}%` : "0%";
    }

    get analyticsMissedRate() {
        const rate = this.state.data.analytics?.missed_rate;
        return rate !== undefined ? `${rate}%` : "0%";
    }

    get peakHourEntries() {
        const hours = (this.state.data.analytics && this.state.data.analytics.peak_hours) || [];
        return hours.map((h, idx) => ({
            id: idx,
            name: h.hour,
            count: h.count,
            action_domain: h.action_domain,
        }));
    }

    get charts() {
        return this.state.data.charts || {};
    }

    get analytics() {
        return this.state.data.analytics || {};
    }

    get topAgents() {
        return this.analytics.top_agents || [];
    }

    get mostContacted() {
        return this.analytics.most_contacted || [];
    }

    getFilters() {
        return {
            date_preset: this.state.datePreset,
            date_from: this.state.dateFrom || false,
            date_to: this.state.dateTo || false,
            user_id: this.state.userId ? parseInt(this.state.userId, 10) : false,
            company_id: this.state.companyId ? parseInt(this.state.companyId, 10) : false,
            direction: this.state.direction || false,
            status: this.state.status || false,
            trend_granularity: this.state.granularity,
        };
    }

    async loadData() {
        if (this._loadDataPromise) {
            return this._loadDataPromise;
        }
        const generation = ++this._loadGeneration;
        this.state.loading = true;
        this._loadDataPromise = (async () => {
            try {
                const data = await this.orm.call(
                    "ringcentral.dashboard",
                    "get_dashboard_data",
                    [],
                    { filters: this.getFilters() }
                );
                if (generation === this._loadGeneration) {
                    this.state.data = data;
                }
            } catch (error) {
                if (generation === this._loadGeneration) {
                    console.error("RingCentral dashboard load error:", error);
                    this.state.data = {
                        kpis: [],
                        charts: {},
                        analytics: {},
                        filter_options: this.state.data.filter_options || {},
                        period_label: "",
                        is_admin: false,
                    };
                }
            } finally {
                if (generation === this._loadGeneration) {
                    this.state.loading = false;
                }
                this._loadDataPromise = null;
            }
        })();
        return this._loadDataPromise;
    }

    _scheduleLoadData() {
        if (this._debounceTimer) {
            clearTimeout(this._debounceTimer);
        }
        this._debounceTimer = setTimeout(() => {
            this._debounceTimer = null;
            this.loadData();
        }, 300);
    }

    async onDatePresetSelect(value) {
        this.state.datePreset = value || "this_month";
        await this.loadData();
    }

    async onDateFromChange(ev) {
        this.state.dateFrom = ev.target.value;
        if (this.state.datePreset === "custom" && this.state.dateFrom && this.state.dateTo) {
            this._scheduleLoadData();
        }
    }

    async onDateToChange(ev) {
        this.state.dateTo = ev.target.value;
        if (this.state.datePreset === "custom" && this.state.dateFrom && this.state.dateTo) {
            this._scheduleLoadData();
        }
    }

    async onUserSelect(value) {
        this.state.userId = value ? String(value) : "";
        await this.loadData();
    }

    async onCompanySelect(value) {
        this.state.companyId = value ? String(value) : "";
        await this.loadData();
    }

    async onDirectionSelect(value) {
        this.state.direction = value || "";
        await this.loadData();
    }

    async onStatusSelect(value) {
        this.state.status = value || "";
        await this.loadData();
    }

    async onGranularitySelect(value) {
        this.state.granularity = value || "day";
        await this.loadData();
    }

    async onClearFilters() {
        this.state.datePreset = "this_month";
        this.state.dateFrom = "";
        this.state.dateTo = "";
        this.state.userId = "";
        this.state.companyId = "";
        this.state.direction = "";
        this.state.status = "";
        this.state.granularity = "day";
        await this.loadData();
    }

    async onRemoveFilterTag(key) {
        switch (key) {
            case "datePreset":
            case "customDate":
                this.state.datePreset = "this_month";
                this.state.dateFrom = "";
                this.state.dateTo = "";
                break;
            case "userId":
                this.state.userId = "";
                break;
            case "companyId":
                this.state.companyId = "";
                break;
            case "direction":
                this.state.direction = "";
                break;
            case "status":
                this.state.status = "";
                break;
            case "granularity":
                this.state.granularity = "day";
                break;
        }
        await this.loadData();
    }

    openCallHistory(domain, name) {
        if (!domain) {
            return;
        }
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "ringcentral.call.history",
            name: name || "Call History",
            views: [[false, "list"], [false, "form"]],
            domain,
        });
    }

    onKpiClick(kpi) {
        this.openCallHistory(kpi.action_domain, kpi.action_name || kpi.label);
    }

    onLeaderboardClick(entry) {
        this.openCallHistory(entry.action_domain, entry.name);
    }

    onSuccessRateClick() {
        const domain = this.state.data.analytics?.success_rate_domain;
        this.openCallHistory(domain, "Answered Calls");
    }

    onMissedRateClick() {
        const domain = this.state.data.analytics?.missed_rate_domain;
        this.openCallHistory(domain, "Missed Calls");
    }

    hasChartData(chart) {
        if (!chart || !chart.labels || !chart.labels.length) {
            return false;
        }
        return (chart.datasets || []).some((ds) => (ds.data || []).some((v) => v > 0));
    }

    hasBarData(chart) {
        if (!chart) {
            return false;
        }
        if (chart.data) {
            return chart.data.some((v) => v > 0);
        }
        return this.hasChartData(chart);
    }

    renderCharts() {
        if (this.state.loading || typeof Chart === "undefined") {
            return;
        }
        const charts = this.state.data.charts || {};

        this._renderCallTrend(charts.call_trend);
        this._renderDirectionBar(charts.direction_bar);
        this._renderStatusDoughnut(charts.status_doughnut);
        this._renderTopUsers(charts.top_users);
        this._renderVolume(charts.call_volume);
        this._renderDuration(charts.duration_trend);
        this._renderMissedAnswered(charts.missed_vs_answered);
    }

    _renderChart(key, canvas, config) {
        if (!canvas) {
            return;
        }
        if (this.chartInstances[key]) {
            this.chartInstances[key].destroy();
        }
        this.chartInstances[key] = new Chart(canvas, config);
    }

    _renderCallTrend(chartData) {
        const canvas = this.callTrendChartRef.el;
        if (!canvas || !chartData?.labels?.length) {
            this._destroyChart("callTrend");
            return;
        }
        const datasets = (chartData.datasets || []).map((ds) => ({
            label: ds.label,
            data: ds.data,
            borderColor: ds.color,
            backgroundColor: `${ds.color}22`,
            fill: true,
            tension: 0.35,
            pointRadius: 3,
            pointHoverRadius: 6,
        }));
        const config = lineChartConfig(chartData.labels, datasets);
        config._actionDomains = chartData.action_domains || [];
        attachChartClick(config, (index) => {
            const domain = config._actionDomains[index];
            this.openCallHistory(domain, "Call Trend");
        });
        this._renderChart("callTrend", canvas, config);
    }

    _renderDirectionBar(chartData) {
        const canvas = this.directionChartRef.el;
        if (!canvas || !chartData?.data?.length) {
            this._destroyChart("direction");
            return;
        }
        const config = barChartConfig(
            chartData.labels,
            chartData.data,
            chartData.colors,
            "Calls"
        );
        config._actionDomains = chartData.action_domains || [];
        attachChartClick(config, (index) => {
            this.openCallHistory(config._actionDomains[index], chartData.labels[index]);
        });
        this._renderChart("direction", canvas, config);
    }

    _renderStatusDoughnut(chartData) {
        const canvas = this.statusChartRef.el;
        if (!canvas || !chartData?.data?.length) {
            this._destroyChart("status");
            return;
        }
        const config = doughnutChartConfig(
            chartData.labels,
            chartData.data,
            chartData.colors
        );
        config._actionDomains = chartData.action_domains || [];
        attachChartClick(config, (index) => {
            this.openCallHistory(config._actionDomains[index], chartData.labels[index]);
        });
        this._renderChart("status", canvas, config);
    }

    _renderTopUsers(chartData) {
        const canvas = this.topUsersChartRef.el;
        if (!canvas || !chartData?.data?.length) {
            this._destroyChart("topUsers");
            return;
        }
        const wrap = canvas.parentElement;
        if (wrap) {
            wrap.style.height = `${Math.max(220, chartData.labels.length * 36)}px`;
        }
        const config = horizontalBarChartConfig(
            chartData.labels,
            chartData.data,
            chartData.data.map((_, i) => ["#714B67", "#17a2b8", "#28a745"][i % 3])
        );
        config._actionDomains = chartData.action_domains || [];
        attachChartClick(config, (index) => {
            this.openCallHistory(config._actionDomains[index], chartData.labels[index]);
        });
        this._renderChart("topUsers", canvas, config);
    }

    _renderVolume(chartData) {
        const canvas = this.volumeChartRef.el;
        if (!canvas || !chartData?.data?.length) {
            this._destroyChart("volume");
            return;
        }
        const config = barChartConfig(chartData.labels, chartData.data, "#714B67", "Calls");
        config._actionDomains = chartData.action_domains || [];
        attachChartClick(config, (index) => {
            this.openCallHistory(config._actionDomains[index], "Call Volume");
        });
        this._renderChart("volume", canvas, config);
    }

    _renderDuration(chartData) {
        const canvas = this.durationChartRef.el;
        if (!canvas || !chartData?.data?.length) {
            this._destroyChart("duration");
            return;
        }
        const config = lineChartConfig(chartData.labels, [{
            label: "Avg duration (s)",
            data: chartData.data,
            borderColor: "#6f42c1",
            backgroundColor: "rgba(111, 66, 193, 0.12)",
            fill: true,
            tension: 0.35,
            pointRadius: 3,
        }]);
        config._actionDomains = chartData.action_domains || [];
        attachChartClick(config, (index) => {
            this.openCallHistory(config._actionDomains[index], "Call Duration");
        });
        this._renderChart("duration", canvas, config);
    }

    _renderMissedAnswered(chartData) {
        const canvas = this.missedAnsweredChartRef.el;
        if (!canvas || !chartData?.data?.length) {
            this._destroyChart("missedAnswered");
            return;
        }
        const config = barChartConfig(
            chartData.labels,
            chartData.data,
            chartData.colors,
            "Calls"
        );
        config._actionDomains = chartData.action_domains || [];
        attachChartClick(config, (index) => {
            this.openCallHistory(config._actionDomains[index], chartData.labels[index]);
        });
        this._renderChart("missedAnswered", canvas, config);
    }

    _destroyChart(key) {
        if (this.chartInstances[key]) {
            this.chartInstances[key].destroy();
            delete this.chartInstances[key];
        }
    }
}

// Primary tag — must match ir.actions.client tag (action_ringcentral_kpi_dashboard).
registry.category("actions").add("ringcentral_kpi_dashboard", RingCentralDashboard);
// Alias for forward-compatible XML references.
registry.category("actions").add("ringcentral_dashboard", RingCentralDashboard);
