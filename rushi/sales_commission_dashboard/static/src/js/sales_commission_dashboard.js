/** @odoo-module */

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useRef, onMounted, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

export class SalesCommissionDash extends Component {
    static props = {
        action: Object,
        actionId: Number,
        updateActionState: Function,
        className: { type: String, optional: true },
        globalState: { type: Object, optional: true },
    };
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            salesCommissionData: [],
            allUsers: [],
            selectedUser: '',
            loading: false,
            isInitialized: false,
            salesperson: false
        });
        // Refs for all tables
        this.commissionSummaryBody = useRef("commissionSummaryBody");
        this.customerCommissionBody = useRef("customerCommissionBody");
        this.monthlyPerformanceBody = useRef("monthlyPerformanceBody");
        this.Paymentduedate = useRef("Paymentduedate");
        this.PendingForDeliveries = useRef("PendingForDeliveries");
        onMounted(async () => {
            setTimeout(() => {
                this.initializeComponent();
            }, 100);
        });
    }
    async loadAllUsers() {
        try {
            const users = await this.orm.searchRead(
                'res.users',
                [
                    ['active', '=', true],
                    ['share', '=', false]  // Only internal users
                ],
                ['name', 'login'],
                {
                    order: 'name asc'
                }
            );
            this.state.allUsers = users;
        } catch (error) {
            console.error('Error loading users:', error);
            this.notification.add(_t("Error loading users"), { type: 'danger' });
        }
    }
    onUserSelectionChange(ev) {
        this.state.selectedUser = ev.target.value;
        // Reload data with selected user filter
        this.loadOtherTablesData();
    }
    onViewModeChange(ev) {
        this.state.salesperson = ev.target.value;
        this.initializeComponent();
    }
    async initializeComponent() {
        this.state.isInitialized = true;
        await this.loadAllUsers(); // Load users first
        await this.loadOtherTablesData();
    }
    loadOtherTablesData() {
        this.loadSalesCommissionData();
        this.renderCustomerCommissionTable();
        this.renderMonthlyPerformanceTable();
        this.renderMonthlyPerformanceTabley();
        this.renderCommissionPlansTable();
    }
    async loadSalesCommissionData() {
        if (!this.state.isInitialized) {
            return;
        }

        try {
            // Build domain based on selected user
            let domain = [];
            if (this.state.selectedUser) {
                domain.push(['user_id', '=', parseInt(this.state.selectedUser)]);
            }

            var commissionRecords = await this.orm.call('sale.commission.report', 'read_group',
             [
                domain,
                ['user_id', 'target_amount', 'achieved', 'commission', 'id'],
                ['user_id',],
            ]);

//            var commissionRecords = commissionRecords.sort((a, b) => b.total_sales - a.total_sales).slice(0, 15);

            const processedData = commissionRecords.map(record => ({
                user_id: record.user_id ? record.user_id[1] : 'N/A',
                target_amount: record.target_amount || 0,
                commission: record.commission || 0,
                achieved: record.achieved || 0
            }));

            this.state.salesCommissionData = processedData;
            this.renderSalesCommissionTable();

        } catch (error) {
            console.error('Error loading sales commission data:', error);
            this.notification.add(_t("Error loading commission data"), { type: 'danger' });

            this.state.salesCommissionData = [
                {
                    user_id: 'Data not Available',
                    target_amount: 750,
                    commission: 750,
                    achieved: 750
                }
            ];
            this.renderSalesCommissionTable();
        }
    }
    renderSalesCommissionTable() {
        try {
            if (!this.commissionSummaryBody || !this.commissionSummaryBody.el) {
                setTimeout(() => this.renderSalesCommissionTable(), 100);
                return;
            }

            const tbody = this.commissionSummaryBody.el;
            tbody.innerHTML = '';

            if (this.state.salesCommissionData.length === 0) {
                tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted">No commission data available</td></tr>';
                return;
            }

            this.state.salesCommissionData.forEach(row => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${row.user_id}</td>
                    <td>${row.target_amount}</td>
                    <td>${row.commission}</td>
                    <td>${row.achieved}</td>
                `;
                tbody.appendChild(tr);
            });
        } catch (error) {
            console.error('Error rendering table:', error);
        }
    }
    async renderMonthlyPerformanceTable() {
        if (!this.monthlyPerformanceBody.el) return;

        try {
            // Build domain with user filter
            let domain = [['state', '=', 'sent']];
            if (this.state.selectedUser) {
                domain.push(['user_id', '=', parseInt(this.state.selectedUser)]);
            }

            const SaleOrder = await this.orm.searchRead(
                "sale.order",
                domain,
                ["name","date_order","partner_id","user_id", "company_id","amount_total"]
            );

            const tbody = this.monthlyPerformanceBody.el;
            tbody.innerHTML = '';

            if (!SaleOrder || SaleOrder.length === 0) {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td colspan="6" class="text-center text-muted">
                        <i class="fa fa-info-circle"></i> No pending quotation found
                    </td>
                `;
                tbody.appendChild(tr);
                return;
            }

            SaleOrder.forEach(Order => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${Order.name || 'N/A'}</td>
                    <td>${Order.date_order.split(' ')[0] || 'N/A'}</td>
                    <td>${Order.partner_id[1] || 'N/A'}</td>
                    <td>${Order.user_id[1] || 'N/A'}</td>
                    <td>${Order.company_id[1] || 'N/A'}</td>
                    <td>${Order.amount_total || 'N/A'}</td>
                `;
                tbody.appendChild(tr);
            });

        } catch (error) {
            console.error('Error loading pending orders:', error);

            const tbody = this.monthlyPerformanceBody.el;
            tbody.innerHTML = '';

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td colspan="6" class="text-center text-danger">
                    <i class="fa fa-exclamation-triangle"></i> Failed to load pending orders
                </td>
            `;
            tbody.appendChild(tr);
        }
    }
    async renderMonthlyPerformanceTabley() {
        if (!this.Paymentduedate.el) return;

        try {
            const today = new Date().toISOString().split('T')[0];

            // Build domain with user filter
            let domain = [
                ['move_type', '=', 'out_invoice'],
                ['payment_state', 'in', ['not_paid', 'partial']],
                ['invoice_date_due', '<', today]
            ];

            if (this.state.selectedUser) {
                domain.push(['invoice_user_id', '=', parseInt(this.state.selectedUser)]);
            }

            const DueInvoice = await this.orm.searchRead(
                "account.move",
                domain,
                ["name","invoice_date_due","invoice_user_id","partner_id", "company_id","amount_residual_signed"]
            );

            const tbody = this.Paymentduedate.el;
            tbody.innerHTML = '';

            if (!DueInvoice || DueInvoice.length === 0) {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td colspan="6" class="text-center text-muted">
                        <i class="fa fa-info-circle"></i> No overdue invoices found
                    </td>
                `;
                tbody.appendChild(tr);
                return;
            }

            DueInvoice.forEach(Order => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${Order.name || 'N/A'}</td>
                    <td>${Order.invoice_date_due || 'N/A'}</td>
                    <td>${Order.invoice_user_id ? Order.invoice_user_id[1] : 'N/A'}</td>
                    <td>${Order.partner_id[1] || 'N/A'}</td>
                    <td>${Order.company_id[1] || 'N/A'}</td>
                    <td>${(Order.amount_residual_signed || 0)}</td>
                `;
                tbody.appendChild(tr);
            });

        } catch (error) {
            console.error('Error loading overdue invoices:', error);

            const tbody = this.Paymentduedate.el;
            tbody.innerHTML = '';

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td colspan="6" class="text-center text-danger">
                    <i class="fa fa-exclamation-triangle"></i> Failed to load overdue invoices
                </td>
            `;
            tbody.appendChild(tr);
        }
    }
    async renderCustomerCommissionTable() {
        if (!this.customerCommissionBody.el) return;

        try {
            let domain = [['customer_rank', '>', 0]];
            if (this.state.selectedUser) {
                domain.push(['user_id', '=', parseInt(this.state.selectedUser)]);
            }
            const SalePartner = await this.orm.call('sale.order', 'read_group',
                 [
                    [],
                    ['partner_id'],
                    ['partner_id'],
                ]);
            if (SalePartner){
                domain.push(['id', 'not in',SalePartner.map(item => item.partner_id[0])]);
            }
            const inactiveCustomers = await this.orm.searchRead('res.partner',
                domain,
                ['name'],
                {
                    order: 'name asc',
                    limit: 15
                }
            );

            const tbody = this.customerCommissionBody.el;
            tbody.innerHTML = '';

            if (!inactiveCustomers || inactiveCustomers.length === 0) {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="text-center text-muted">
                        <i class="fa fa-info-circle"></i> No inactive customers found
                    </td>
                `;
                tbody.appendChild(tr);
                return;
            }

            inactiveCustomers.forEach(customer => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${customer.name || 'N/A'}</td>
                `;
                tbody.appendChild(tr);
            });

        } catch (error) {
            console.error('Error loading inactive customers:', error);

            const tbody = this.customerCommissionBody.el;
            tbody.innerHTML = '';

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="text-center text-danger">
                    <i class="fa fa-exclamation-triangle"></i> Failed to load inactive customers
                </td>
            `;
            tbody.appendChild(tr);
        }
    }
    async renderCommissionPlansTable() {
        if (!this.PendingForDeliveries.el) return;
            let domain = [['picking_type_id.code', '=', 'outgoing'],['state', 'in', ['confirmed', 'assigned']]];
            if (this.state.selectedUser) {
                var SoPickingRecords = await this.orm.call('sale.order', 'read_group',
                 [
                    [['user_id', '=', parseInt(this.state.selectedUser)], ['state', '=', 'sale']],
                    ['id'],
                    ['id']
                ]);
                if (SoPickingRecords){
                    domain.push(['sale_id', 'in', SoPickingRecords.map(record => record.id[0])]);
                }
            }

        const DeliveriesData = await this.orm.searchRead(
                "stock.picking",
                 domain,
                 ["name","scheduled_date","partner_id","id"]
        );

        const tbody = this.PendingForDeliveries.el;
        tbody.innerHTML = '';

        DeliveriesData.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${row.name}</td>
                <td>${row.scheduled_date}</td>
                <td>${row.partner_id[1] || 'N/A'}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'AED',
            minimumFractionDigits: 2
        }).format(amount);
    }

    exportData() {
        this.notification.add(_t("Export functionality coming soon"), { type: 'info' });
    }
}

SalesCommissionDash.template = "sales_commission_dashboard.SalesCommissionDashTemplate";
registry.category("actions").add("sales_commission_dashboard_widget", SalesCommissionDash);