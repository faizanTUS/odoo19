# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
import calendar

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class PettyCashVoucher(models.Model):
    _name = "petty.cash.voucher"
    _description = "Petty Cash Voucher"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        default="/",
        readonly=True,
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    currency_id = fields.Many2one(
        related="fund_id.currency_id",
        store=True,
    )
    fund_id = fields.Many2one(
        "petty.cash.fund",
        required=True,
        ondelete="restrict",
        domain=lambda self: [('company_id', '=', self.env.company.id)] if self.env.company else [],
        tracking=True,
        check_company=False,
    )
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        tracking=True,
        domain=lambda self: [('company_id', '=', self.env.company.id)] if self.env.company else [],
        check_company=False,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Requester User",
        default=lambda self: self.env.user,
        required=True,
        index=True,
    )
    date = fields.Date(
        default=fields.Date.context_today,
        required=True,
        tracking=True,
    )
    category_id = fields.Many2one(
        "petty.cash.category",
        string="Expense Category",
        domain=lambda self: [('company_id', '=', self.env.company.id)],
        tracking=True,
    )
    amount = fields.Monetary(
        currency_field="currency_id",
        required=True,
        tracking=True,
    )
    description = fields.Text(tracking=True)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("under_approval", "Under Approval"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("paid", "Paid"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    approval_line_ids = fields.One2many(
        "petty.cash.approval.line",
        "voucher_id",
        string="Approvals",
    )
    current_approver_id = fields.Many2one(
        "res.users",
        string="Current Approver",
        compute="_compute_current_approver",
        store=False,
    )
    user_can_approve = fields.Boolean(
        compute="_compute_user_can_approve",
    )

    payment_move_id = fields.Many2one(
        "account.move",
        string="Journal Entry",
        readonly=True,
        copy=False,
        check_company=True,
    )
    is_reconciled = fields.Boolean(
        string="Reconciled",
        default=False,
        tracking=True,
        help="Mark when matched with bank/cash statement or internal control.",
    )
    has_receipt = fields.Boolean(
        compute="_compute_has_receipt",
        store=True,
    )
    attachment_ids = fields.Many2many(
        "ir.attachment",
        string="Receipts",
        relation="petty_cash_voucher_attachment_rel",
        column1="voucher_id",
        column2="attachment_id",
    )
    receipt_count = fields.Integer(compute="_compute_receipt_count")

    @api.depends("attachment_ids")
    def _compute_receipt_count(self):
        for rec in self:
            rec.receipt_count = len(rec.attachment_ids)

    require_receipt = fields.Boolean(
        compute="_compute_require_receipt",
        store=True,
    )

    days_pending = fields.Integer(
        string="Days Pending",
        compute="_compute_aging_fields",
        store=True,
    )
    aging_bucket = fields.Selection(
        [
            ("0_7", "0-7 Days"),
            ("8_15", "8-15 Days"),
            ("16_30", "16-30 Days"),
            ("31_plus", "31+ Days"),
        ],
        compute="_compute_aging_fields",
        store=True,
    )

    rejection_reason = fields.Text(readonly=True, copy=False)

    _sql_constraints = [
        ("petty_cash_voucher_amount_positive", "CHECK(amount > 0)", "Amount must be positive."),
    ]

    @api.depends("approval_line_ids", "approval_line_ids.state", "approval_line_ids.sequence")
    def _compute_current_approver(self):
        for rec in self:
            pending = rec.approval_line_ids.filtered(lambda l: l.state == "pending").sorted("sequence")
            rec.current_approver_id = pending[:1].user_id if pending else False

    @api.depends("state", "current_approver_id")
    def _compute_user_can_approve(self):
        uid = self.env.uid
        for rec in self:
            rec.user_can_approve = bool(
                rec.state == "under_approval"
                and rec.current_approver_id
                and rec.current_approver_id.id == uid
            )

    @api.depends("fund_id", "fund_id.policy_id")
    def _compute_require_receipt(self):
        for rec in self:
            policy = rec.fund_id.policy_id
            rec.require_receipt = bool(policy and getattr(policy, "require_receipt", False))

    @api.depends("attachment_ids")
    def _compute_has_receipt(self):
        for rec in self:
            rec.has_receipt = bool(rec.attachment_ids)

    def action_view_attachments(self):
        self.ensure_one()
        return {
            "name": _("Receipts"),
            "domain": [("id", "in", self.attachment_ids.ids)],
            "res_model": "ir.attachment",
            "type": "ir.actions.act_window",
            "view_mode": "kanban,tree,form",
            "context": "{'default_res_model': '%s', 'default_res_id': %s}" % (self._name, self.id),
            "help": _('<p class="o_view_nocontent_smiling_face">Upload receipts</p>'),
        }

    @api.depends("date", "state", "is_reconciled")
    def _compute_aging_fields(self):
        today = fields.Date.today()
        for rec in self:
            if rec.state in ("cancelled", "rejected", "draft") or (rec.state == "paid" and rec.is_reconciled):
                rec.days_pending = 0
                rec.aging_bucket = False
                continue
            if not rec.date:
                rec.days_pending = 0
                rec.aging_bucket = False
                continue
            delta = (today - rec.date).days
            rec.days_pending = max(0, delta)
            if delta <= 7:
                rec.aging_bucket = "0_7"
            elif delta <= 15:
                rec.aging_bucket = "8_15"
            elif delta <= 30:
                rec.aging_bucket = "16_30"
            else:
                rec.aging_bucket = "31_plus"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("petty.cash.voucher") or "/"
        return super().create(vals_list)

    def _get_expense_account(self):
        self.ensure_one()
        if self.category_id.expense_account_id:
            return self.category_id.expense_account_id
        if self.fund_id.default_expense_account_id:
            return self.fund_id.default_expense_account_id
        raise UserError(
            _("Configure an expense account on the category %(cat)s or a default on fund %(fund)s.")
            % {"cat": self.category_id.display_name, "fund": self.fund_id.display_name}
        )

    def _check_policy_limits(self):
        for rec in self:
            policy = rec.fund_id.policy_id
            if not policy:
                continue
            if (
                policy.max_amount_per_voucher
                and float_compare(
                    rec.amount,
                    policy.max_amount_per_voucher,
                    precision_rounding=rec.currency_id.rounding,
                )
                > 0
            ):
                raise ValidationError(
                    _("Voucher amount exceeds policy maximum (%s).")
                    % (policy.max_amount_per_voucher,)
                )
            if policy.category_ids and rec.category_id not in policy.category_ids:
                raise ValidationError(_("Selected category is not allowed by this fund's policy."))

            Voucher = self.env["petty.cash.voucher"]
            if policy.daily_limit_per_employee:
                start = rec.date
                daily = Voucher.read_group(
                    [
                        ("id", "!=", rec.id),
                        ("employee_id", "=", rec.employee_id.id),
                        ("fund_id", "=", rec.fund_id.id),
                        ("date", "=", start),
                        ("state", "not in", ("draft", "cancelled", "rejected")),
                    ],
                    ["amount:sum"],
                    [],
                )
                total = (daily[0]["amount"] if daily else 0.0) + rec.amount
                if (
                    float_compare(
                        total,
                        policy.daily_limit_per_employee,
                        precision_rounding=rec.currency_id.rounding,
                    )
                    > 0
                ):
                    raise ValidationError(_("Daily spend limit exceeded for this employee."))

            if policy.monthly_limit_per_employee:
                month_start = rec.date.replace(day=1)
                last_day = calendar.monthrange(rec.date.year, rec.date.month)[1]
                month_end = rec.date.replace(day=last_day)
                monthly = Voucher.read_group(
                    [
                        ("id", "!=", rec.id),
                        ("employee_id", "=", rec.employee_id.id),
                        ("fund_id", "=", rec.fund_id.id),
                        ("date", ">=", month_start),
                        ("date", "<=", month_end),
                        ("state", "not in", ("draft", "cancelled", "rejected")),
                    ],
                    ["amount:sum"],
                    [],
                )
                total = (monthly[0]["amount"] if monthly else 0.0) + rec.amount
                if (
                    float_compare(
                        total,
                        policy.monthly_limit_per_employee,
                        precision_rounding=rec.currency_id.rounding,
                    )
                    > 0
                ):
                    raise ValidationError(_("Monthly spend limit exceeded for this employee."))

    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                continue
            if not rec.category_id:
                raise UserError(_("Please set an expense category before submitting."))
            rec._check_policy_limits()
            rules = self.env["petty.cash.approval.rule"].search(
                [
                    ("fund_id", "=", rec.fund_id.id),
                    ("active", "=", True),
                    ("amount_from", "<=", rec.amount),
                    ("amount_to", ">=", rec.amount),
                ],
                order="sequence, id",
            )
            rec.state = "under_approval" if rules else "approved"
            if rules:
                for rule in rules:
                    self.env["petty.cash.approval.line"].create(
                        {
                            "voucher_id": rec.id,
                            "sequence": rule.sequence,
                            "rule_id": rule.id,
                            "user_id": rule.approver_id.id,
                            "state": "pending",
                        }
                    )
                rec.message_post(body=_("Voucher submitted for approval."))
            else:
                rec.message_post(body=_("No approval rules matched; voucher is approved."))

    def action_approve(self):
        for rec in self:
            if rec.state != "under_approval":
                continue
            line = rec.approval_line_ids.filtered(
                lambda l: l.state == "pending" and l.user_id == self.env.user
            ).sorted("sequence")[:1]
            if not line:
                raise UserError(_("You are not the current approver for this voucher."))
            line.write({"state": "approved", "approval_date": fields.Datetime.now()})
            pending = rec.approval_line_ids.filtered(lambda l: l.state == "pending")
            if not pending:
                rec.state = "approved"
                rec.message_post(body=_("All approval levels cleared."))

    def action_reject_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Reject Voucher"),
            "res_model": "petty.cash.approval.reject.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_voucher_id": self.id},
        }

    def action_reject(self, reason):
        self.ensure_one()
        if self.state != "under_approval":
            raise UserError(_("Only vouchers under approval can be rejected."))
        self.write({"state": "rejected", "rejection_reason": reason})
        self.approval_line_ids.filtered(lambda l: l.state == "pending").write({"state": "cancelled"})
        self.message_post(body=_("Rejected: %s") % (reason or "",))

    def action_pay(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError(_("Only approved vouchers can be paid."))
            expense_account = rec._get_expense_account()
            partner = rec.employee_id.work_contact_id
            move = self.env["account.move"].create(
                {
                    "move_type": "entry",
                    "journal_id": rec.fund_id.journal_id.id,
                    "date": rec.date,
                    "ref": rec.name,
                    "company_id": rec.company_id.id,
                    "petty_cash_fund_id": rec.fund_id.id,
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "account_id": expense_account.id,
                                "debit": rec.amount,
                                "credit": 0.0,
                                "name": rec.description or rec.name,
                                "partner_id": partner.id if partner else False,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "account_id": rec.fund_id.petty_cash_account_id.id,
                                "debit": 0.0,
                                "credit": rec.amount,
                                "name": rec.description or rec.name,
                            },
                        ),
                    ],
                }
            )
            move.action_post()
            rec.payment_move_id = move
            rec.state = "paid"
            rec.message_post(body=_("Payment posted: %s") % (move.display_name,))
            # Trigger recompute of fund metrics by clearing the cache
            rec.fund_id.invalidate_recordset(["balance", "available_balance", "monthly_spent"])
            rec.fund_id._compute_balance_metrics()

    def action_mark_reconciled(self):
        self.write({"is_reconciled": True})

    def action_cancel(self):
        for rec in self:
            if rec.state not in ("draft", "submitted", "under_approval", "approved"):
                raise UserError(_("Only open vouchers can be cancelled."))
            rec.state = "cancelled"
            rec.approval_line_ids.filtered(lambda l: l.state == "pending").write({"state": "cancelled"})

    def action_draft(self):
        self.filtered(lambda v: v.state == "cancelled").write({"state": "draft"})


class PettyCashApprovalLine(models.Model):
    _name = "petty.cash.approval.line"
    _description = "Petty Cash Approval Line"
    _order = "sequence, id"

    voucher_id = fields.Many2one(
        "petty.cash.voucher",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(default=10)
    rule_id = fields.Many2one("petty.cash.approval.rule", ondelete="set null")
    user_id = fields.Many2one("res.users", required=True)
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
        required=True,
    )
    approval_date = fields.Datetime()
