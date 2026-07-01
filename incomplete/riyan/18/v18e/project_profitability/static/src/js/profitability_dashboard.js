/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

export class ProfitabilityDashboard extends Component {
    static template = "project_profitability.ProfitabilityDashboard";

    setup() {
        this.actionService = useService("action");
        this.notification = useService("notification");
        this.state = useState({
            loading: true,
            data: null,
            error: null,
            expandedCustomers: {},
            sortBy: "customer",
            sortDirection: "asc",
        });
        this.sortOptions = [
            { value: "customer", label: "Customer" },
            { value: "lead_name", label: "Lead / Opportunity" },
            { value: "lead_value", label: "Lead Expected Revenue" },
            { value: "so_total", label: "SO Total" },
            { value: "revenue", label: "Revenue" },
            { value: "cost", label: "Expense" },
            { value: "margin", label: "Margin" },
            { value: "margin_percentage", label: "Margin %" },
            { value: "progress", label: "Progress" },
        ];

        onWillStart(() => this.loadDashboard());
    }

    toggleCustomer(customerKey) {
        const expanded = { ...this.state.expandedCustomers };
        expanded[customerKey] = !expanded[customerKey];
        this.state.expandedCustomers = expanded;
    }

    isCustomerExpanded(customerKey) {
        return !!this.state.expandedCustomers[customerKey];
    }

    getStatusBadgeClass(stageName) {
        // Distinct colors per stage - hash stage name to palette index
        const palette = [
            'badge-status-1',  // blue
            'badge-status-2',  // green
            'badge-status-3',  // purple
            'badge-status-4',  // orange
            'badge-status-5',  // teal
            'badge-status-6',  // pink
            'badge-status-7',  // amber
            'badge-status-8',  // indigo
        ];
        if (!stageName) return 'bg-secondary';
        let hash = 0;
        for (let i = 0; i < stageName.length; i++) hash += stageName.charCodeAt(i);
        return palette[Math.abs(hash) % palette.length];
    }

    getSortedLeadData() {
        const groups = this.state.data?.lead_so_details_by_customer || [];
        if (!groups.length) return [];
        const sortBy = this.state.sortBy || "customer";
        const asc = this.state.sortDirection !== "desc";

        const getRowValue = (row, key) => {
            switch (key) {
                case "lead_name": return (row.lead_name || row.project_name || "").toLowerCase();
                case "lead_value": return row.lead_value ?? 0;
                case "so_total": return row.so_total ?? 0;
                case "revenue": return row.revenue?.recognized ?? 0;
                case "cost": return row.costs?.total ?? 0;
                case "margin": return row.profitability?.margin ?? 0;
                case "margin_percentage": return row.profitability?.margin_percentage ?? 0;
                case "progress": return row.progress ?? 0;
                default: return 0;
            }
        };

        const getGroupValue = (group, key) => {
            if (key === "customer" || key === "lead_name") return (group.customer || "").toLowerCase();
            const totals = this.getCustomerTotals(group);
            return totals[key] ?? 0;
        };

        return groups.map((group) => {
            const projects = [...(group.projects || [])];
            if (sortBy !== "customer") {
                projects.sort((a, b) => {
                    const va = getRowValue(a, sortBy);
                    const vb = getRowValue(b, sortBy);
                    const cmp = typeof va === "string" ? va.localeCompare(vb) : va - vb;
                    return asc ? cmp : -cmp;
                });
            }
            return { ...group, projects };
        }).sort((a, b) => {
            const va = sortBy === "customer" ? (a.customer || "").toLowerCase() : getGroupValue(a, sortBy);
            const vb = sortBy === "customer" ? (b.customer || "").toLowerCase() : getGroupValue(b, sortBy);
            const cmp = typeof va === "string" ? va.localeCompare(vb) : va - vb;
            return asc ? cmp : -cmp;
        });
    }

    setSortBy(value) {
        if (this.state.sortBy === value) {
            this.state.sortDirection = this.state.sortDirection === "asc" ? "desc" : "asc";
        } else {
            this.state.sortBy = value;
            this.state.sortDirection = "asc";
        }
    }

    getCustomerTotals(group) {
        if (!group?.projects?.length) {
            return {
                lead_value: 0, so_total: 0, revenue: 0, cost: 0,
                budget_revenue: 0, budget_cost: 0, margin: 0,
                margin_percentage: 0, progress: 0,
            };
        }
        const totals = group.projects.reduce(
            (acc, row) => ({
                lead_value: acc.lead_value + (row.lead_value ?? 0),
                so_total: acc.so_total + (row.so_total ?? 0),
                revenue: acc.revenue + (row.revenue?.recognized ?? 0),
                cost: acc.cost + (row.costs?.total ?? 0),
                budget_revenue: acc.budget_revenue + (row.budget?.revenue ?? 0),
                budget_cost: acc.budget_cost + (row.budget?.cost ?? 0),
                margin: acc.margin + (row.profitability?.margin ?? 0),
            }),
            { lead_value: 0, so_total: 0, revenue: 0, cost: 0, budget_revenue: 0, budget_cost: 0, margin: 0 }
        );
        totals.margin_percentage = totals.revenue ? (totals.margin / totals.revenue * 100) : 0;
        totals.progress = totals.so_total ? (totals.revenue / totals.so_total * 100) : 0;
        return totals;
    }

    async loadDashboard() {
        this.state.loading = true;
        this.state.error = null;
        try {
            const data = await rpc("/project/profitability/dashboard", {});
            this.state.data = data;
        } catch (err) {
            this.state.error = err?.message || "Failed to load dashboard data";
            this.state.data = null;
        } finally {
            this.state.loading = false;
        }
    }

    formatCurrency(value) {
        if (value == null || isNaN(value)) return "0.00";
        const symbol = this.state.data?.currency_symbol || "";
        return `${symbol} ${Number(value).toLocaleString("en-US", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        })}`;
    }

    formatPercent(value) {
        if (value == null || isNaN(value)) return "0%";
        return `${Number(value).toFixed(1)}%`;
    }

    onRefresh() {
        this.loadDashboard();
    }

    onExport() {
        window.open("/project/profitability/export", "_blank");
    }

    onOpenLead(leadId) {
        if (!leadId) return;
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "crm.lead",
            res_id: leadId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("profitability_dashboard_action", ProfitabilityDashboard);
