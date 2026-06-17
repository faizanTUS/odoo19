/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

class PettyCashDashboard extends Component {
    static template = "tus_petty_cash_management.PettyCashDashboard";
    static props = { ...standardActionServiceProps };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.state = useState({ data: null, loading: true });

        onWillStart(async () => {
            const data = await this.orm.call("petty.cash.fund", "get_dashboard_kpis", []);
            this.state.data = data;
            this.state.loading = false;
        });
    }

    formatMoney(amount) {
        const d = this.state.data;
        if (!d) {
            return "";
        }
        const n = Number(amount || 0).toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
        return `${d.currency_symbol || ""} ${n}`;
    }

    openFunds() {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Petty Cash Funds",
            res_model: "petty.cash.fund",
            views: [
                [false, "tree"],
                [false, "form"],
            ],
            target: 'current',
        });
    }

    openVouchers(domain = []) {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Vouchers",
            res_model: "petty.cash.voucher",
            views: [
                [false, "tree"],
                [false, "form"],
                [false, "graph"],
                [false, "pivot"],
            ],
            domain: domain.length ? domain : [],
            context: { search_default_group_state: 1 },
            target: 'current',
        });
    }

    openReplenishments() {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Replenishments",
            res_model: "petty.cash.replenishment",
            views: [
                [false, "tree"],
                [false, "form"],
            ],
            domain: [["state", "in", ["draft", "submitted", "approved"]]],
            target: 'current',
        });
    }

    openCriticalFunds() {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Critical Funds",
            res_model: "petty.cash.fund",
            views: [
                [false, "tree"],
                [false, "form"],
            ],
            domain: [["is_critical", "=", true]],
            target: 'current',
        });
    }

    openPaidVouchers() {
        this.openVouchers([["state", "=", "paid"]]);
    }

    openDraftVouchers() {
        this.openVouchers([["state", "=", "draft"]]);
    }

    openUnreconciled() {
        this.openVouchers([
            ["state", "=", "paid"],
            ["is_reconciled", "=", false],
        ]);
    }

    openMissingReceipts() {
        this.openVouchers([
            ["require_receipt", "=", true],
            ["has_receipt", "=", false],
        ]);
    }

    openCancelledVouchers() {
        this.openVouchers([["state", "=", "cancelled"]]);
    }
}

registry.category("actions").add("petty_cash_dashboard", PettyCashDashboard);
