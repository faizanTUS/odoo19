/** @odoo-module */

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useRef, onMounted, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

function partnerLabel(partnerId) {
    return partnerId && partnerId[1] ? partnerId[1] : "N/A";
}

function userLabel(userId) {
    return userId && userId[1] ? userId[1] : "N/A";
}

function companyLabel(companyId) {
    return companyId && companyId[1] ? companyId[1] : "N/A";
}

export class SalesCommissionDash extends Component {
    static props = {
        action: Object,
        actionId: Number,
        updateActionState: { type: Function, optional: true },
        className: { type: String, optional: true },
        globalState: { type: Object, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            allUsers: [],
            selectedUser: "",
        });
        this.commissionSummaryBody = useRef("commissionSummaryBody");
        this.customerCommissionBody = useRef("customerCommissionBody");
        this.monthlyPerformanceBody = useRef("monthlyPerformanceBody");
        this.paymentDueDateBody = useRef("Paymentduedate");
        this.pendingDeliveriesBody = useRef("PendingForDeliveries");
        onMounted(() => {
            Promise.resolve().then(() => this.initializeComponent());
        });
    }

    async loadAllUsers() {
        try {
            const users = await this.orm.searchRead(
                "res.users",
                [
                    ["active", "=", true],
                    ["share", "=", false],
                ],
                ["name", "login"],
                { order: "name asc" }
            );
            this.state.allUsers = users;
        } catch (error) {
            console.error("Error loading users:", error);
            this.notification.add(_t("Error loading users"), { type: "danger" });
        }
    }

    onUserSelectionChange(ev) {
        this.state.selectedUser = ev.target.value;
        this.loadOtherTablesData();
    }

    async initializeComponent() {
        await this.loadAllUsers();
        await this.loadOtherTablesData();
    }

    async loadOtherTablesData() {
        await Promise.all([
            this.renderCustomerCommissionTable(),
            this.renderPendingQuotationsTable(),
            this.renderOverdueInvoicesTable(),
            this.renderPendingDeliveriesTable(),
        ]);
    }

    async renderPendingQuotationsTable() {
        if (!this.monthlyPerformanceBody.el) {
            return;
        }
        try {
            const domain = [["state", "=", "sent"]];
            if (this.state.selectedUser) {
                domain.push(["user_id", "=", parseInt(this.state.selectedUser, 10)]);
            }
            const saleOrders = await this.orm.searchRead(
                "sale.order",
                domain,
                ["name", "date_order", "partner_id", "user_id", "company_id", "amount_total"]
            );
            const tbody = this.monthlyPerformanceBody.el;
            tbody.innerHTML = "";
            if (!saleOrders || !saleOrders.length) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center text-muted">
                            <i class="fa fa-info-circle"></i> No pending quotation found
                        </td>
                    </tr>`;
                return;
            }
            for (const order of saleOrders) {
                const tr = document.createElement("tr");
                const dateStr = order.date_order ? String(order.date_order).split(" ")[0] : "N/A";
                tr.innerHTML = `
                    <td>${order.name || "N/A"}</td>
                    <td>${dateStr}</td>
                    <td>${partnerLabel(order.partner_id)}</td>
                    <td>${userLabel(order.user_id)}</td>
                    <td>${companyLabel(order.company_id)}</td>
                    <td>${order.amount_total != null ? order.amount_total : "N/A"}</td>
                `;
                tbody.appendChild(tr);
            }
        } catch (error) {
            console.error("Error loading pending orders:", error);
            const tbody = this.monthlyPerformanceBody.el;
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-danger">
                        <i class="fa fa-exclamation-triangle"></i> Failed to load pending orders
                    </td>
                </tr>`;
        }
    }

    async renderOverdueInvoicesTable() {
        if (!this.paymentDueDateBody.el) {
            return;
        }
        try {
            const today = new Date().toISOString().split("T")[0];
            const domain = [
                ["move_type", "=", "out_invoice"],
                ["payment_state", "in", ["not_paid", "partial"]],
                ["invoice_date_due", "<", today],
            ];
            if (this.state.selectedUser) {
                domain.push(["invoice_user_id", "=", parseInt(this.state.selectedUser, 10)]);
            }
            const dueInvoices = await this.orm.searchRead(
                "account.move",
                domain,
                ["name", "invoice_date_due", "invoice_user_id", "partner_id", "company_id", "amount_residual_signed"]
            );
            const tbody = this.paymentDueDateBody.el;
            tbody.innerHTML = "";
            if (!dueInvoices || !dueInvoices.length) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center text-muted">
                            <i class="fa fa-info-circle"></i> No overdue invoices found
                        </td>
                    </tr>`;
                return;
            }
            for (const inv of dueInvoices) {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${inv.name || "N/A"}</td>
                    <td>${inv.invoice_date_due || "N/A"}</td>
                    <td>${inv.invoice_user_id ? inv.invoice_user_id[1] : "N/A"}</td>
                    <td>${partnerLabel(inv.partner_id)}</td>
                    <td>${companyLabel(inv.company_id)}</td>
                    <td>${inv.amount_residual_signed != null ? inv.amount_residual_signed : 0}</td>
                `;
                tbody.appendChild(tr);
            }
        } catch (error) {
            console.error("Error loading overdue invoices:", error);
            const tbody = this.paymentDueDateBody.el;
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-danger">
                        <i class="fa fa-exclamation-triangle"></i> Failed to load overdue invoices
                    </td>
                </tr>`;
        }
    }

    async renderCustomerCommissionTable() {
        if (!this.customerCommissionBody.el) {
            return;
        }
        try {
            const domain = [["customer_rank", ">", 0]];
            if (this.state.selectedUser) {
                domain.push(["user_id", "=", parseInt(this.state.selectedUser, 10)]);
            }
            const salePartnerGroups = await this.orm.call("sale.order", "read_group", [
                [],
                ["partner_id"],
                ["partner_id"],
            ]);
            if (salePartnerGroups && salePartnerGroups.length) {
                const partnerIds = salePartnerGroups
                    .map((item) => (item.partner_id && item.partner_id[0] ? item.partner_id[0] : null))
                    .filter(Boolean);
                if (partnerIds.length) {
                    domain.push(["id", "not in", partnerIds]);
                }
            }
            const inactiveCustomers = await this.orm.searchRead("res.partner", domain, ["name"], {
                order: "name asc",
                limit: 15,
            });
            const tbody = this.customerCommissionBody.el;
            tbody.innerHTML = "";
            if (!inactiveCustomers || !inactiveCustomers.length) {
                tbody.innerHTML = `
                    <tr>
                        <td class="text-center text-muted">
                            <i class="fa fa-info-circle"></i> No inactive customers found
                        </td>
                    </tr>`;
                return;
            }
            for (const customer of inactiveCustomers) {
                const tr = document.createElement("tr");
                tr.innerHTML = `<td>${customer.name || "N/A"}</td>`;
                tbody.appendChild(tr);
            }
        } catch (error) {
            console.error("Error loading inactive customers:", error);
            const tbody = this.customerCommissionBody.el;
            tbody.innerHTML = `
                <tr>
                    <td class="text-center text-danger">
                        <i class="fa fa-exclamation-triangle"></i> Failed to load inactive customers
                    </td>
                </tr>`;
        }
    }

    async renderPendingDeliveriesTable() {
        if (!this.pendingDeliveriesBody.el) {
            return;
        }
        try {
            let domain = [
                ["picking_type_id.code", "=", "outgoing"],
                ["state", "in", ["confirmed", "assigned"]],
            ];
            if (this.state.selectedUser) {
                const saleOrders = await this.orm.searchRead(
                    "sale.order",
                    [
                        ["user_id", "=", parseInt(this.state.selectedUser, 10)],
                        ["state", "=", "sale"],
                    ],
                    ["id"]
                );
                if (saleOrders && saleOrders.length) {
                    domain.push(["sale_id", "in", saleOrders.map((r) => r.id)]);
                } else {
                    domain.push(["sale_id", "in", []]);
                }
            }
            const deliveriesData = await this.orm.searchRead(
                "stock.picking",
                domain,
                ["name", "scheduled_date", "partner_id", "id"]
            );
            const tbody = this.pendingDeliveriesBody.el;
            tbody.innerHTML = "";
            if (!deliveriesData || !deliveriesData.length) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="3" class="text-center text-muted">
                            <i class="fa fa-info-circle"></i> No pending deliveries found
                        </td>
                    </tr>`;
                return;
            }
            for (const row of deliveriesData) {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${row.name}</td>
                    <td>${row.scheduled_date || "N/A"}</td>
                    <td>${partnerLabel(row.partner_id)}</td>
                `;
                tbody.appendChild(tr);
            }
        } catch (error) {
            console.error("Error loading pending deliveries:", error);
            const tbody = this.pendingDeliveriesBody.el;
            tbody.innerHTML = `
                <tr>
                    <td colspan="3" class="text-center text-danger">
                        <i class="fa fa-exclamation-triangle"></i> Failed to load pending deliveries
                    </td>
                </tr>`;
        }
    }
}

SalesCommissionDash.template = "sales_commission_dashboard.SalesCommissionDashTemplate";
registry.category("actions").add("sales_commission_dashboard_widget", SalesCommissionDash);
