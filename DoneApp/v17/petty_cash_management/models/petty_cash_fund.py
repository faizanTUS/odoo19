# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from datetime import date

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class PettyCashFund(models.Model):
    _name = "petty.cash.fund"
    _description = "Petty Cash Fund"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(tracking=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    manager_id = fields.Many2one(
        "res.users",
        string="Fund Custodian",
        tracking=True,
        domain="[('share', '=', False)]",
        help="Person responsible for the physical cash box and approvals oversight.",
    )
    policy_id = fields.Many2one(
        "petty.cash.policy",
        string="Spend Policy",
        domain=lambda self: [('company_id', '=', self.env.company.id)] if self.env.company else [],
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Petty Cash Journal",
        required=True,
        domain="[('type', 'in', ('cash', 'general')), ('company_id', '=', company_id)]",
        check_company=False,
        help="Journal used for petty cash movements (payments and replenishments).",
    )
    petty_cash_account_id = fields.Many2one(
        "account.account",
        string="Petty Cash GL Account",
        required=True,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
        check_company=False,
    )
    default_expense_account_id = fields.Many2one(
        "account.account",
        string="Default Expense Account",
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
        help="Used when the expense category has no account configured.",
    )
    source_bank_journal_id = fields.Many2one(
        "account.journal",
        string="Replenishment Source Journal",
        domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]",
        check_company=False,
        help="Bank or cash journal used when topping up this fund.",
    )
    min_balance = fields.Monetary(
        string="Minimum Balance (Alert)",
        currency_field="currency_id",
        help="When current balance is at or below this amount, the fund is flagged as critical.",
    )
    auto_replenish = fields.Boolean(
        string="Suggest Replenishment",
        help="When critical, create an activity for the custodian (cron also logs chatter).",
    )
    replenishment_target_amount = fields.Monetary(
        currency_field="currency_id",
        help="Suggested top-up amount when requesting replenishment.",
    )
    physical_balance = fields.Monetary(
        currency_field="currency_id",
        tracking=True,
        help="Last physical count — optional; used for expected vs actual variance on the dashboard.",
    )
    last_count_date = fields.Date(string="Last Physical Count Date")

    approval_rule_ids = fields.One2many(
        "petty.cash.approval.rule",
        "fund_id",
        string="Approval Matrix",
    )

    balance = fields.Monetary(
        compute="_compute_balance_metrics",
        currency_field="currency_id",
        store=False,
    )
    available_balance = fields.Monetary(
        compute="_compute_balance_metrics",
        currency_field="currency_id",
        store=False,
    )
    monthly_spent = fields.Monetary(
        compute="_compute_balance_metrics",
        currency_field="currency_id",
        store=False,
    )
    is_critical = fields.Boolean(
        compute="_compute_balance_metrics",
        store=False,
    )
    expected_vs_actual_variance = fields.Monetary(
        compute="_compute_balance_metrics",
        currency_field="currency_id",
        store=False,
        string="Count Variance",
    )

    voucher_ids = fields.One2many("petty.cash.voucher", "fund_id", string="Vouchers")
    replenishment_ids = fields.One2many(
        "petty.cash.replenishment",
        "fund_id",
        string="Replenishments",
    )
    voucher_count = fields.Integer(compute="_compute_counts")
    replenishment_count = fields.Integer(compute="_compute_counts")

    @api.depends("voucher_ids", "replenishment_ids")
    def _compute_counts(self):
        for rec in self:
            rec.voucher_count = len(rec.voucher_ids)
            rec.replenishment_count = len(rec.replenishment_ids)

    @api.depends(
        "petty_cash_account_id",
        "company_id",
        "currency_id",
        "physical_balance",
        "min_balance",
        "voucher_ids.state",
        "voucher_ids.amount",
    )
    def _compute_balance_metrics(self):
        today = date.today()
        month_start = today.replace(day=1)
        Voucher = self.env["petty.cash.voucher"]
        for fund in self:
            balance = 0.0
            if fund.petty_cash_account_id:
                domain = [
                    ("account_id", "=", fund.petty_cash_account_id.id),
                    ("parent_state", "=", "posted"),
                    ("company_id", "=", fund.company_id.id),
                ]
                data = self.env["account.move.line"].read_group(
                    domain,
                    ["balance:sum"],
                    [],
                )
                balance = data[0]["balance"] if data else 0.0
            fund.balance = balance

            # Available balance = GL Balance - Pending Vouchers (submitted/approved but not yet paid)
            pending_vouchers = Voucher.read_group(
                [
                    ("fund_id", "=", fund.id),
                    ("state", "in", ("submitted", "under_approval", "approved")),
                ],
                ["amount:sum"],
                [],
            )
            pending_amount = pending_vouchers[0]["amount"] if pending_vouchers else 0.0
            fund.available_balance = balance - pending_amount

            spent = Voucher.read_group(
                [
                    ("fund_id", "=", fund.id),
                    ("state", "=", "paid"),
                    ("date", ">=", month_start),
                    ("date", "<=", today),
                ],
                ["amount:sum"],
                [],
            )
            fund.monthly_spent = spent[0]["amount"] if spent else 0.0
            fund.is_critical = bool(
                fund.min_balance
                and not float_is_zero(fund.min_balance, precision_rounding=fund.currency_id.rounding)
                and float_compare(balance, fund.min_balance, precision_rounding=fund.currency_id.rounding)
                <= 0
            )
            if fund.physical_balance is not False and fund.physical_balance is not None:
                fund.expected_vs_actual_variance = (fund.physical_balance or 0.0) - balance
            else:
                fund.expected_vs_actual_variance = 0.0

    @api.model
    def get_dashboard_kpis(self):
        """Used by the backend dashboard client action."""
        self.check_access_rights("read")
        funds = self.search([("company_id", "in", self.env.companies.ids)])
        Voucher = self.env["petty.cash.voucher"]
        Rep = self.env["petty.cash.replenishment"]
        today = date.today()
        month_start = today.replace(day=1)
        currency = self.env.company.currency_id

        # GL Balance already includes deductions if posted correctly.
        total_cash = sum(funds.mapped("balance"))

        # Available balance logic: Total Cash (GL) - Pending Vouchers
        available = sum(funds.mapped("available_balance"))

        monthly_domain = [
            ("company_id", "in", self.env.companies.ids),
            ("state", "=", "paid"),
            ("date", ">=", month_start),
        ]
        monthly_data = Voucher.read_group(monthly_domain, ["amount:sum"], [])
        monthly_spent = monthly_data[0]["amount"] if monthly_data else 0.0

        draft_count = Voucher.search_count(
            [("company_id", "in", self.env.companies.ids), ("state", "=", "draft")]
        )
        rep_pending = Rep.search_count(
            [
                ("company_id", "in", self.env.companies.ids),
                ("state", "in", ("draft", "submitted", "approved")),
            ]
        )
        unreconciled = Voucher.search_count(
            [
                ("company_id", "in", self.env.companies.ids),
                ("state", "=", "paid"),
                ("is_reconciled", "=", False),
            ]
        )
        cancelled_count = Voucher.search_count(
            [
                ("company_id", "in", self.env.companies.ids),
                ("state", "=", "cancelled"),
            ]
        )
        critical = funds.filtered(lambda f: f.is_critical)
        missing_receipt = Voucher.search_count(
            [
                ("company_id", "in", self.env.companies.ids),
                ("state", "in", ("submitted", "under_approval", "approved", "paid")),
                ("require_receipt", "=", True),
                ("has_receipt", "=", False),
            ]
        )
        variance_abs = sum(abs(f.expected_vs_actual_variance or 0) for f in funds)
        return {
            "currency_id": currency.id,
            "currency_symbol": currency.symbol,
            "total_cash": total_cash,
            "available_balance": available,
            "monthly_spent": monthly_spent,
            "draft_vouchers": draft_count,
            "replenishments_pending": rep_pending,
            "unreconciled": unreconciled,
            "cancelled_vouchers": cancelled_count,
            "critical_funds": len(critical),
            "missing_receipts": missing_receipt,
            "variance_total": variance_abs,
        }

    @api.model
    def _cron_check_critical_balances(self):
        """Notify custodians when funds are at or below minimum balance."""
        funds = self.search([("auto_replenish", "=", True), ("active", "=", True)])
        for fund in funds:
            fund.invalidate_recordset(["balance", "is_critical"])
            if fund.is_critical and fund.manager_id:
                note = _(
                    "Petty cash balance (%(bal)s) is at or below the minimum (%(min)s). Consider replenishment."
                ) % {"bal": fund.balance, "min": fund.min_balance}
                fund.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=fund.manager_id.id,
                    summary=_("Critical petty cash balance: %s") % fund.name,
                    note=note,
                )

    def action_view_vouchers(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Vouchers"),
            "res_model": "petty.cash.voucher",
            "view_mode": "tree,form",
            "domain": [("fund_id", "=", self.id)],
            "context": {"default_fund_id": self.id},
        }

    def action_view_replenishments(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Replenishments"),
            "res_model": "petty.cash.replenishment",
            "view_mode": "tree,form",
            "domain": [("fund_id", "=", self.id)],
            "context": {"default_fund_id": self.id},
        }

    def action_request_replenishment(self):
        self.ensure_one()
        if not self.source_bank_journal_id:
            raise UserError(_("Configure a replenishment source journal on the fund first."))
        return {
            "type": "ir.actions.act_window",
            "name": _("New Replenishment"),
            "res_model": "petty.cash.replenishment",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_fund_id": self.id,
                "default_amount": self.replenishment_target_amount or self.min_balance * 2 if self.min_balance else 0.0,
            },
        }
