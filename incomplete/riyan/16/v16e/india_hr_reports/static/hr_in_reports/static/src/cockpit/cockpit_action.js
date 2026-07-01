/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { loadJS } from "@web/core/assets";
import { registry } from "@web/core/registry";
import { Component, xml, useRef, onWillStart, useState, useEffect } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

// Odoo 16 compatibility shims for helpers introduced in v17+:
// colors/colors, browser/cookie, and record_selectors/multi_record_selector.
const _COCKPIT_PALETTE = [
    "#714B67", "#5e60ce", "#2a9d8f", "#e9c46a",
    "#f4a261", "#e76f51", "#264653", "#1d3557",
    "#06a77d", "#ef476f",
];
function getColor(index) {
    return _COCKPIT_PALETTE[(Math.max(1, index) - 1) % _COCKPIT_PALETTE.length];
}
function getCustomColor(_scheme, lightColor /*, darkColor */) {
    return lightColor;
}
function _readCookie(name) {
    const parts = (document.cookie || "").split(";");
    for (const p of parts) {
        const [k, v] = p.split("=").map((s) => (s || "").trim());
        if (k === name) {
            return v;
        }
    }
    return "";
}
const colorScheme = _readCookie("color_scheme");

function formatIsoDate(d) {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${day}`;
}

function defaultDateRange() {
    const today = new Date();
    const from = new Date(today);
    from.setDate(from.getDate() - 30);
    return { dateFrom: formatIsoDate(from), dateTo: formatIsoDate(today) };
}

function activeCompanyIds(userService, companyService) {
    return (
        userService?.context?.allowed_company_ids ||
        companyService?.allowedCompanyIds ||
        companyService?.activeCompanyIds ||
        [companyService?.currentCompany?.id].filter(Boolean)
    );
}

class CockpitChart extends Component {
    static template = xml`
        <div class="o_hr_dash-chart-wrap">
            <div class="o_hr_in_cockpit_chart position-relative" t-att-class="props.chart?.half_donut ? 'o_hr_dash-chart-half' : ''">
                <canvas t-ref="canvas"/>
            </div>
        </div>
    `;
    static props = { chart: Object };

    setup() {
        this.canvasRef = useRef("canvas");
        this.chartInstance = null;
        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
        });
        useEffect(
            () => {
                this.renderChart();
                return () => {
                    if (this.chartInstance) {
                        this.chartInstance.destroy();
                        this.chartInstance = null;
                    }
                };
            },
            () => [this.props.chart],
        );
    }

    renderChart() {
        const Chart = globalThis.Chart;
        if (!Chart || !this.canvasRef.el) {
            return;
        }
        const c = this.props.chart || {};
        const labels = c.labels || [];
        const rawDatasets = c.datasets || [];
        const ctype = c.type === "doughnut" ? "doughnut" : c.type;
        if (ctype === "doughnut" && (!labels.length || !(rawDatasets[0]?.data || []).length)) {
            return;
        }
        if (this.chartInstance) {
            this.chartInstance.destroy();
            this.chartInstance = null;
        }
        const grid = getCustomColor(colorScheme, "#e9ecef", "#3C3E4B");
        const tick = getCustomColor(colorScheme, "#495057", "#E4E4E4");
        let datasets = [];
        if (ctype === "doughnut") {
            const ds0 = rawDatasets[0] || { label: "", data: [] };
            datasets = [
                {
                    label: ds0.label,
                    data: ds0.data,
                    backgroundColor: labels.map((_, j) => getColor(j + 1, colorScheme, "odoo")),
                    borderColor: getCustomColor(colorScheme, "#ffffff", "#1f1f1f"),
                    borderWidth: 2,
                },
            ];
        } else {
            datasets = rawDatasets.map((ds, i) => {
                const base = getColor(i + 1, colorScheme, "odoo");
                return {
                    label: ds.label,
                    data: ds.data,
                    borderColor: base,
                    backgroundColor: c.type === "line" ? `${base}33` : `${base}bb`,
                    borderWidth: 2,
                    tension: c.type === "line" ? 0.25 : 0,
                    fill: Boolean(ds.fill),
                };
            });
        }
        const options = {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: c.horizontal ? "y" : "x",
            plugins: {
                legend: { display: ctype === "doughnut" || rawDatasets.length > 1 },
            },
            scales:
                ctype === "doughnut"
                    ? {}
                    : {
                          x: {
                              ticks: { color: tick, maxRotation: c.horizontal ? 0 : 45, minRotation: 0 },
                              grid: { color: grid },
                          },
                          y: {
                              beginAtZero: true,
                              ticks: { color: tick },
                              grid: { color: grid },
                          },
                      },
        };
        if (ctype === "doughnut") {
            options.cutout = c.half_donut ? "68%" : "58%";
            if (c.half_donut) {
                options.rotation = -Math.PI / 2;
                options.circumference = Math.PI;
            }
        }
        this.chartInstance = new Chart(this.canvasRef.el, {
            type: ctype === "doughnut" ? "doughnut" : c.type,
            data: { labels, datasets },
            options,
        });
    }
}

class CockpitDashCard extends Component {
    static template = xml`
        <div class="o_hr_dash-card" t-att-class="props.card.footer_action ? 'o_hr_dash-card--clickable' : ''">
            <div
                class="o_hr_dash-card-main"
                t-att-class="props.card.footer_action ? 'o_hr_dash-card-main--clickable' : ''"
                t-on-click="onCardMainClick"
                t-att-tabindex="props.card.footer_action ? 0 : -1"
                t-att-role="props.card.footer_action ? 'button' : undefined"
                t-on-keydown="onCardMainKeydown"
            >
                <div class="o_hr_dash-card-head d-flex justify-content-between align-items-start">
                    <h3 class="o_hr_dash-card-title" t-esc="props.card.title"/>
                </div>
                <div class="o_hr_dash-card-body">
                    <t t-if="props.card.card_type === 'chart' and props.card.chart">
                        <CockpitChart chart="props.card.chart"/>
                    </t>
                    <t t-if="props.card.card_type === 'metric_grid' and props.card.metrics">
                        <div class="o_hr_dash-metric-grid">
                            <t t-foreach="props.card.metrics" t-as="m" t-key="m_index">
                                <div class="o_hr_dash-metric-cell">
                                    <div class="o_hr_dash-metric-label" t-esc="m.label"/>
                                    <div class="o_hr_dash-metric-value" t-esc="m.value"/>
                                </div>
                            </t>
                        </div>
                    </t>
                    <t t-if="props.card.card_type === 'simple_list'">
                        <ul class="o_hr_dash-simple-list list-unstyled mb-0">
                            <t t-foreach="props.card.list or []" t-as="row" t-key="row_index">
                                <li class="d-flex justify-content-between py-1 border-bottom border-light">
                                    <span class="text-muted" t-esc="row.label"/>
                                    <span class="fw-semibold" t-esc="row.value"/>
                                </li>
                            </t>
                        </ul>
                    </t>
                    <t t-if="props.card.card_type === 'map_list'">
                        <t t-if="props.card.rows and props.card.rows.length">
                            <ul class="o_hr_dash-map-list list-unstyled mb-0">
                                <t t-foreach="props.card.rows" t-as="row" t-key="row_index">
                                    <li class="d-flex justify-content-between align-items-center py-2 border-bottom border-light">
                                        <span>
                                            <span class="o_hr_dash-flag me-2" t-if="row.code" t-esc="flagEmoji(row.code)"/>
                                            <t t-esc="row.label"/>
                                        </span>
                                        <span class="badge rounded-pill bg-light text-dark border" t-esc="row.count"/>
                                    </li>
                                </t>
                            </ul>
                        </t>
                        <t t-else="">
                            <p class="small text-muted mb-0" t-if="props.card.empty_hint" t-esc="props.card.empty_hint"/>
                            <p class="small text-muted mb-0" t-else="">—</p>
                        </t>
                    </t>
                    <t t-if="props.card.card_type === 'funnel'">
                        <div class="o_hr_dash-funnel">
                            <t t-foreach="props.card.funnel or []" t-as="st" t-key="st_index">
                                <div class="o_hr_dash-funnel-row">
                                    <div class="o_hr_dash-funnel-bar" t-attf-style="width: #{st.width_pct}%;">
                                        <span class="o_hr_dash-funnel-label" t-esc="st.label"/>
                                        <span class="o_hr_dash-funnel-count" t-esc="st.count"/>
                                    </div>
                                </div>
                            </t>
                        </div>
                    </t>
                    <t t-if="props.card.card_type === 'gauge' and props.card.gauge">
                        <div class="o_hr_dash-gauge-wrap">
                            <div class="o_hr_dash-gauge" t-attf-style="--pct: #{gaugePct};">
                                <div class="o_hr_dash-gauge-inner">
                                    <span class="o_hr_dash-gauge-val" t-esc="formatGauge(props.card.gauge)"/>
                                </div>
                            </div>
                            <p class="small text-muted text-center mt-2 mb-0" t-if="props.card.gauge.hint" t-esc="props.card.gauge.hint"/>
                        </div>
                    </t>
                </div>
            </div>
            <div class="o_hr_dash-card-foot text-end" t-if="props.card.footer">
                <a
                    t-if="props.card.footer_action"
                    href="#"
                    class="o_hr_dash-card-link small"
                    t-on-click.stop="onFooterClick"
                    t-esc="props.card.footer"
                />
                <span t-else="" class="small text-muted" t-esc="props.card.footer"/>
            </div>
        </div>
    `;
    static components = { CockpitChart };
    static props = { card: Object };

    setup() {
        this.action = useService("action");
        this.notification = useService("notification");
    }

    async openCardAction() {
        const act = this.props.card.footer_action;
        if (!act) {
            return;
        }
        try {
            await this.action.doAction(act);
        } catch (e) {
            console.error(e);
            this.notification.add(_t("Could not open the linked screen."), { type: "danger" });
        }
    }

    async onCardMainClick(ev) {
        if (!this.props.card.footer_action) {
            return;
        }
        await this.openCardAction();
    }

    async onCardMainKeydown(ev) {
        if (!this.props.card.footer_action) {
            return;
        }
        if (ev.key === "Enter" || ev.key === " ") {
            ev.preventDefault();
            await this.openCardAction();
        }
    }

    async onFooterClick(ev) {
        ev.preventDefault();
        await this.openCardAction();
    }

    flagEmoji(code) {
        if (!code || code.length !== 2) {
            return "";
        }
        const A = 0x1f1e6;
        const c = code.toUpperCase();
        return String.fromCodePoint(A + c.charCodeAt(0) - 65) + String.fromCodePoint(A + c.charCodeAt(1) - 65);
    }

    formatGauge(g) {
        if (!g || g.value === null || g.value === undefined) {
            return g && g.display ? g.display : "—";
        }
        const v = g.value;
        const m = g.max;
        if (m <= 10) {
            return `${v}/${m}`;
        }
        return `${Math.round(v)}%`;
    }

    get gaugePct() {
        const g = this.props.card.gauge;
        if (!g || !g.max || g.value === null || g.value === undefined) {
            return 0;
        }
        return Math.min(100, Math.round((100 * g.value) / g.max));
    }
}

export class HrInReportsCockpit extends Component {
    static components = { CockpitChart, CockpitDashCard };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.action = useService("action");
        this.userService = useService("user");
        this.companyService = useService("company");
        this.strings = {
            branch: _t("Companies"),
            customize: _t("Customize"),
            apply: _t("Apply"),
            loading: _t("Loading…"),
            filterEmployees: _t("Employees"),
            filterDepartments: _t("Departments"),
            filterJobs: _t("Job positions"),
            clearScope: _t("Clear HR scope"),
            phEmployees: _t("Add employees…"),
            phDepartments: _t("Add departments…"),
            phJobs: _t("Add job positions…"),
            calendar: _t("Calendar"),
            birthdays: _t("Upcoming birthdays"),
            quickLinks: _t("Quick links"),
            presence: _t("Global presence"),
            schema: _t("Schema"),
        };
        const dr = defaultDateRange();
        this.state = useState({
            payload: null,
            error: null,
            loading: true,
            dateFrom: dr.dateFrom,
            dateTo: dr.dateTo,
            employeeIds: [],
            departmentIds: [],
            jobIds: [],
            showCustomize: false,
        });

        onWillStart(async () => {
            await this.loadPayload();
        });
    }

    get companyDomain() {
        const cids = activeCompanyIds(this.userService, this.companyService);
        return ["|", ["company_id", "=", false], ["company_id", "in", cids]];
    }

    get employeeDomain() {
        return this.companyDomain;
    }

    get departmentDomain() {
        return this.companyDomain;
    }

    get jobDomain() {
        return this.companyDomain;
    }

    get layout() {
        return this.state.payload?.layout || null;
    }

    get employeeIdsInput() {
        return (this.state.employeeIds || []).join(", ");
    }

    get departmentIdsInput() {
        return (this.state.departmentIds || []).join(", ");
    }

    get jobIdsInput() {
        return (this.state.jobIds || []).join(", ");
    }

    _parseIdList(raw) {
        return String(raw || "")
            .split(/[,\s]+/)
            .map((x) => parseInt(x, 10))
            .filter((n) => Number.isFinite(n) && n > 0);
    }

    onEmployeeIdsChange(ev) {
        this.state.employeeIds = this._parseIdList(ev.target.value);
    }

    onDepartmentIdsChange(ev) {
        this.state.departmentIds = this._parseIdList(ev.target.value);
    }

    onJobIdsChange(ev) {
        this.state.jobIds = this._parseIdList(ev.target.value);
    }

    async onClearHrScope() {
        this.state.employeeIds = [];
        this.state.departmentIds = [];
        this.state.jobIds = [];
        await this.loadPayload();
    }

    toggleCustomize() {
        this.state.showCustomize = !this.state.showCustomize;
    }

    async loadPayload() {
        this.state.loading = true;
        this.state.error = null;
        try {
            const companyIds = activeCompanyIds(this.userService, this.companyService);
            const payload = await this.orm.call("hr.in.cockpit", "get_dashboard_payload", [
                {
                    date_from: this.state.dateFrom,
                    date_to: this.state.dateTo,
                    company_ids: companyIds,
                    employee_ids: this.state.employeeIds,
                    department_ids: this.state.departmentIds,
                    job_ids: this.state.jobIds,
                },
            ]);
            this.state.payload = payload;
        } catch (e) {
            this.state.error = String(e.message || e);
            this.notification.add(_t("Could not load HR cockpit metrics."), {
                type: "danger",
            });
        } finally {
            this.state.loading = false;
        }
    }

    async onApplyFilters() {
        await this.loadPayload();
    }

    onDateFromChange(ev) {
        this.state.dateFrom = ev.target.value;
    }

    onDateToChange(ev) {
        this.state.dateTo = ev.target.value;
    }

    async onQuickLink(ev, link) {
        ev.preventDefault();
        if (!link?.action_id) {
            return;
        }
        try {
            await this.action.doAction(link.action_id);
        } catch {
            this.notification.add(_t("This shortcut is not available."), { type: "warning" });
        }
    }

    async onKpiClick(ev, k) {
        if (!k?.action) {
            return;
        }
        ev.preventDefault();
        try {
            await this.action.doAction(k.action);
        } catch (e) {
            console.error(e);
            this.notification.add(_t("Could not open the linked screen."), { type: "danger" });
        }
    }

    async onKpiKeydown(ev, k) {
        if (!k?.action) {
            return;
        }
        if (ev.key === "Enter" || ev.key === " ") {
            ev.preventDefault();
            await this.onKpiClick(ev, k);
        }
    }

    calendarCells() {
        const ref = this.state.dateTo || this.state.dateFrom;
        const d = ref ? new Date(`${ref}T12:00:00`) : new Date();
        const y = d.getFullYear();
        const m = d.getMonth();
        const first = new Date(y, m, 1);
        const startPad = (first.getDay() + 6) % 7;
        const daysInMonth = new Date(y, m + 1, 0).getDate();
        const cells = [];
        for (let i = 0; i < startPad; i++) {
            cells.push({ label: "", muted: true });
        }
        for (let day = 1; day <= daysInMonth; day++) {
            cells.push({ label: String(day), muted: false, today: this._isToday(y, m, day) });
        }
        while (cells.length % 7 !== 0 || cells.length < 35) {
            cells.push({ label: "", muted: true });
        }
        return cells;
    }

    _isToday(y, month, day) {
        const t = new Date();
        return t.getFullYear() === y && t.getMonth() === month && t.getDate() === day;
    }

    calDayClass(c) {
        let cls = "o_hr_dash-cal-day";
        if (c.muted) {
            cls += " text-muted o_hr_dash-cal-muted";
        }
        if (c.today) {
            cls += " o_hr_dash-cal-today";
        }
        return cls;
    }

    static template = xml`
        <div class="o_hr_in_reports_cockpit o_action o_hr_dash-root d-flex flex-column h-100 overflow-hidden">
            <div class="o_hr_dash-toolbar flex-shrink-0 bg-view border-bottom px-3 py-3">
                <div class="d-flex flex-wrap align-items-center justify-content-between gap-3">
                    <div>
                        <h1 class="h4 mb-1" t-if="layout">
                            <t t-esc="layout.greeting.prefix"/>,
                            <span class="fw-semibold" t-esc="layout.greeting.name"/>
                        </h1>
                        <div class="text-muted small" t-if="layout?.period_label" t-esc="layout.period_label"/>
                    </div>
                    <div class="d-flex flex-wrap align-items-center gap-2">
                        <div class="d-flex align-items-center gap-1">
                            <input type="date" class="form-control form-control-sm" t-att-value="state.dateFrom" t-on-change="onDateFromChange"/>
                            <span class="text-muted">–</span>
                            <input type="date" class="form-control form-control-sm" t-att-value="state.dateTo" t-on-change="onDateToChange"/>
                        </div>
                        <button type="button" class="btn btn-primary btn-sm" t-on-click="onApplyFilters">
                            <t t-esc="strings.apply"/>
                        </button>
                        <button type="button" class="btn btn-outline-secondary btn-sm" t-on-click="toggleCustomize">
                            <i class="fa fa-sliders me-1"/><t t-esc="strings.customize"/>
                        </button>
                    </div>
                </div>
                <div class="mt-3 pt-3 border-top" t-if="state.showCustomize">
                    <div class="row g-2 align-items-end">
                        <div class="col-12 col-lg-4">
                            <label class="form-label small text-muted mb-1" t-esc="strings.filterEmployees"/>
                            <input type="text" class="form-control form-control-sm"
                                   t-att-value="employeeIdsInput"
                                   t-on-change="(ev) => this.onEmployeeIdsChange(ev)"
                                   t-att-placeholder="strings.phEmployees + ' (IDs, comma separated)'"/>
                        </div>
                        <div class="col-12 col-lg-4">
                            <label class="form-label small text-muted mb-1" t-esc="strings.filterDepartments"/>
                            <input type="text" class="form-control form-control-sm"
                                   t-att-value="departmentIdsInput"
                                   t-on-change="(ev) => this.onDepartmentIdsChange(ev)"
                                   t-att-placeholder="strings.phDepartments + ' (IDs, comma separated)'"/>
                        </div>
                        <div class="col-12 col-lg-3">
                            <label class="form-label small text-muted mb-1" t-esc="strings.filterJobs"/>
                            <input type="text" class="form-control form-control-sm"
                                   t-att-value="jobIdsInput"
                                   t-on-change="(ev) => this.onJobIdsChange(ev)"
                                   t-att-placeholder="strings.phJobs + ' (IDs, comma separated)'"/>
                        </div>
                        <div class="col-12 col-lg-1">
                            <button type="button" class="btn btn-link btn-sm px-0" t-on-click="onClearHrScope">
                                <t t-esc="strings.clearScope"/>
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="o_hr_dash-body flex-grow-1 overflow-auto bg-100">
                <t t-if="state.loading">
                    <div class="text-center py-5 text-muted">
                        <i class="fa fa-circle-o-notch fa-spin fa-2x mb-3 d-block"/>
                        <span t-esc="strings.loading"/>
                    </div>
                </t>
                <t t-elif="state.error">
                    <div class="alert alert-danger m-3" role="alert"><t t-esc="state.error"/></div>
                </t>
                <t t-elif="!layout">
                    <div class="alert alert-warning m-3" role="alert">
                        Dashboard layout is unavailable. Please upgrade the <code>hr_in_reports</code> module.
                    </div>
                </t>
                <t t-elif="layout">
                    <div class="o_hr_dash-kpis row row-cols-2 row-cols-md-3 row-cols-xl-5 g-3 p-3 pb-0">
                        <t t-foreach="layout.kpis" t-as="k" t-key="k.key">
                            <div class="col">
                                <div
                                    t-attf-class="o_hr_dash-kpi o_hr_dash-kpi--#{k.accent} #{k.action ? 'o_hr_dash-kpi--clickable' : ''}"
                                    t-on-click="(ev) => this.onKpiClick(ev, k)"
                                    t-on-keydown="(ev) => this.onKpiKeydown(ev, k)"
                                    t-att-tabindex="k.action ? 0 : -1"
                                    t-att-role="k.action ? 'button' : undefined"
                                >
                                    <div class="o_hr_dash-kpi-label" t-esc="k.label"/>
                                    <div class="o_hr_dash-kpi-value" t-esc="k.value"/>
                                </div>
                            </div>
                        </t>
                    </div>

                    <div class="o_hr_dash-main p-3">
                        <div class="o_hr_dash-grid">
                            <div class="o_hr_dash-columns">
                                <t t-foreach="layout.columns" t-as="col" t-key="col_index">
                                    <div class="o_hr_dash-col">
                                        <t t-foreach="col" t-as="card" t-key="card.id">
                                            <CockpitDashCard card="card"/>
                                        </t>
                                    </div>
                                </t>
                            </div>
                            <aside class="o_hr_dash-sidebar">
                                <div class="o_hr_dash-card mb-3">
                                    <div class="o_hr_dash-card-head">
                                        <h3 class="o_hr_dash-card-title" t-esc="strings.calendar"/>
                                    </div>
                                    <div class="o_hr_dash-card-body">
                                        <div class="o_hr_dash-cal-grid">
                                            <t t-foreach="['M','T','W','T','F','S','S']" t-as="d" t-key="d_index">
                                                <span class="o_hr_dash-cal-dow text-muted small" t-esc="d"/>
                                            </t>
                                            <t t-foreach="calendarCells()" t-as="c" t-key="c_index">
                                                <span
                                                    class="o_hr_dash-cal-day"
                                                    t-att-class="calDayClass(c)"
                                                    t-esc="c.label"
                                                />
                                            </t>
                                        </div>
                                    </div>
                                </div>
                                <div class="o_hr_dash-card mb-3">
                                    <div class="o_hr_dash-card-head">
                                        <h3 class="o_hr_dash-card-title" t-esc="strings.birthdays"/>
                                    </div>
                                    <div class="o_hr_dash-card-body">
                                        <t t-if="layout.sidebar.birthdays and layout.sidebar.birthdays.length">
                                            <ul class="list-unstyled mb-0 small">
                                                <t t-foreach="layout.sidebar.birthdays" t-as="b" t-key="b_index">
                                                    <li class="d-flex justify-content-between py-1 border-bottom border-light">
                                                        <span t-esc="b.name"/>
                                                        <span class="text-muted" t-esc="b.day"/>
                                                    </li>
                                                </t>
                                            </ul>
                                        </t>
                                        <t t-else="">
                                            <p class="small text-muted mb-0">—</p>
                                        </t>
                                    </div>
                                </div>
                                <div class="o_hr_dash-card">
                                    <div class="o_hr_dash-card-head">
                                        <h3 class="o_hr_dash-card-title" t-esc="strings.quickLinks"/>
                                    </div>
                                    <div class="o_hr_dash-card-body">
                                        <div class="o_hr_dash-quicklinks">
                                            <t t-foreach="layout.sidebar.quick_links" t-as="ql" t-key="ql_index">
                                                <a href="#" class="o_hr_dash-quicklink" t-on-click="(ev) => this.onQuickLink(ev, ql)">
                                                    <i t-attf-class="fa #{ql.icon}"/>
                                                    <span t-esc="ql.label"/>
                                                </a>
                                            </t>
                                        </div>
                                    </div>
                                </div>
                            </aside>
                        </div>
                    </div>

                    <footer class="o_hr_dash-footer border-top bg-view px-3 py-3" t-if="layout.footer_presence and layout.footer_presence.length">
                        <div class="small text-muted text-uppercase mb-2" t-esc="strings.presence"/>
                        <div class="d-flex flex-wrap gap-3 align-items-center">
                            <t t-foreach="layout.footer_presence" t-as="p" t-key="p_index">
                                <span class="o_hr_dash-presence-pill badge rounded-pill bg-light text-dark border px-3 py-2">
                                    <t t-esc="p.label"/> · <t t-esc="p.count"/>
                                </span>
                            </t>
                        </div>
                    </footer>
                    <div class="px-3 pb-3 small text-muted">
                        <t t-esc="strings.schema"/> v<t t-esc="state.payload?.meta?.schema_version || 0"/>
                    </div>
                </t>
            </div>
        </div>
    `;

    static props = {
        action: { type: Object, optional: true },
        actionId: { type: Number, optional: true },
        className: { type: String, optional: true },
        globalState: { type: Object, optional: true },
        state: { type: Object, optional: true },
        resId: { type: [Number, Boolean], optional: true },
        updateActionState: { type: Function, optional: true },
    };
}

registry.category("actions").add("india_hr_reports.cockpit", HrInReportsCockpit);
