# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class TusPdcPayment(models.Model):
    _name = "tus.pdc.payment"
    _description = "Post Dated Cheque Payment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(string="PDC Reference", readonly=True, copy=False, default="/", tracking=True)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("registered", "Registered"),
            ("done", "Collected"),
            ("bounce", "Bounced"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    pdc_type = fields.Selection(
        [("customer", "Customer PDC"), ("vendor", "Vendor PDC")],
        required=True,
        tracking=True,
    )

    partner_id = fields.Many2one("res.partner", required=True, tracking=True, index=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id", readonly=True, store=True)

    date = fields.Date(string="PDC Registration Date", default=fields.Date.context_today, required=True, tracking=True)
    cheque_date = fields.Date(string="Cheque Date", required=True, tracking=True)
    cheque_number = fields.Char(string="Cheque Number", required=True, tracking=True)
    bank_name = fields.Char(string="Bank Name", tracking=True)

    amount = fields.Monetary(string="PDC Amount", required=True, tracking=True)

    invoice_ids = fields.Many2many(
        "account.move",
        "tus_pdc_invoice_rel",
        "pdc_id",
        "move_id",
        string="Invoices",
        domain="[('move_type', 'in', ('out_invoice','out_refund','in_invoice','in_refund')), ('state','=','posted'), ('payment_state','in',('not_paid','partial'))]",
    )

    move_pdc_id = fields.Many2one("account.move", string="PDC Journal Entry", readonly=True, copy=False)
    move_collection_id = fields.Many2one("account.move", string="Collection Journal Entry", readonly=True, copy=False)
    move_bounce_id = fields.Many2one("account.move", string="Bounce Journal Entry", readonly=True, copy=False)

    note = fields.Text(string="Internal Notes")

    days_overdue = fields.Integer(compute="_compute_days_overdue", store=True)
    status_date = fields.Date(compute="_compute_status_date", store=True)

    @api.depends("cheque_date", "state")
    def _compute_status_date(self):
        for rec in self:
            rec.status_date = rec.cheque_date if rec.state in ("registered", "done") else rec.date

    @api.depends("status_date", "state")
    def _compute_days_overdue(self):
        today = fields.Date.today()
        for rec in self:
            if rec.state == "registered" and rec.status_date and today > rec.status_date:
                rec.days_overdue = (today - rec.status_date).days
            else:
                rec.days_overdue = 0

    @api.constrains("amount", "invoice_ids", "partner_id")
    def _check_amount_partner(self):
        for rec in self:
            if rec.amount <= 0:
                raise UserError(_("PDC amount must be strictly positive."))
            if rec.invoice_ids:
                partner = rec.partner_id.commercial_partner_id
                if any(inv.partner_id.commercial_partner_id != partner for inv in rec.invoice_ids):
                    raise UserError(_("All invoices on a PDC must belong to the same commercial partner."))

    @api.onchange("invoice_ids")
    def _onchange_invoice_ids(self):
        for rec in self:
            if rec.invoice_ids:
                residual = sum(rec.invoice_ids.mapped("amount_residual"))
                if not rec.amount or abs(rec.amount - residual) < 0.01:
                    rec.amount = residual

    def _next_sequence(self):
        return self.env["ir.sequence"].next_by_code("tus.pdc.payment") or "/"

    def _get_pdc_accounts_and_journals(self):
        self.ensure_one()
        c = self.company_id

        if self.pdc_type == "customer":
            pdc_account = c.customer_pdc_account_id
            bounce_account = c.customer_pdc_bounce_account_id
            reg_journal = c.customer_pdc_journal_id
            origin_type = "asset_receivable"
        else:
            pdc_account = c.vendor_pdc_account_id
            bounce_account = c.vendor_pdc_bounce_account_id
            reg_journal = c.vendor_pdc_journal_id
            origin_type = "liability_payable"

        bank_journal = c.pdc_bank_journal_id

        if not pdc_account or not reg_journal:
            raise UserError(_("Please configure PDC accounts and PDC journals in Accounting Settings."))

        if not bank_journal:
            raise UserError(_("Please configure the PDC Bank Journal in Accounting Settings."))

        if not bank_journal.default_account_id:
            raise UserError(_("Bank Journal must have a Bank Account set."))

        return pdc_account, bounce_account, reg_journal, bank_journal, origin_type

    def _reconcile_with_invoices(self):
        for rec in self:
            if not rec.move_pdc_id or not rec.invoice_ids:
                continue

            partner = rec.partner_id.commercial_partner_id
            account_type = "asset_receivable" if rec.pdc_type == "customer" else "liability_payable"

            invoice_lines = rec.invoice_ids.line_ids.filtered(
                lambda l: l.partner_id == partner and l.account_id.account_type == account_type and not l.reconciled
            )
            pdc_lines = rec.move_pdc_id.line_ids.filtered(
                lambda l: l.partner_id == partner and l.account_id.account_type == account_type and not l.reconciled
            )

            lines = invoice_lines + pdc_lines
            if lines:
                lines.reconcile()

    def _reconcile_pdc_account(self, pdc_account):
        for rec in self:
            if not rec.move_pdc_id or not rec.move_collection_id:
                continue
            lines = (rec.move_pdc_id.line_ids + rec.move_collection_id.line_ids).filtered(
                lambda l: l.account_id == pdc_account and not l.reconciled
            )
            if lines:
                lines.reconcile()

    def action_register(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only Draft PDCs can be registered."))
            if not rec.invoice_ids:
                raise UserError(_("Please link at least one invoice."))

            pdc_account, _bounce, reg_journal, _bank_journal, origin_type = rec._get_pdc_accounts_and_journals()

            if rec.name == "/":
                rec.name = rec._next_sequence()

            company = rec.company_id
            partner = rec.partner_id.commercial_partner_id

            amount_company = rec.amount
            if rec.currency_id != company.currency_id:
                amount_company = rec.currency_id._convert(rec.amount, company.currency_id, company, rec.date)

            partner_lines = rec.invoice_ids.line_ids.filtered(
                lambda l: l.partner_id == partner and l.account_id.account_type == origin_type and not l.reconciled
            )
            if not partner_lines:
                raise UserError(_("No open receivable/payable lines found for the selected invoices."))

            origin_account = partner_lines[0].account_id

            # Customer: Dr PDC / Cr AR
            # Vendor:   Dr AP  / Cr PDC
            if rec.pdc_type == "customer":
                debit_account = pdc_account
                credit_account = origin_account
            else:
                debit_account = origin_account
                credit_account = pdc_account

            move = self.env["account.move"].create({
                "move_type": "entry",
                "date": rec.date,
                "ref": rec.name,
                "journal_id": reg_journal.id,  # Miscellaneous
                "company_id": company.id,
                "line_ids": [
                    (0, 0, {
                        "name": rec.name,
                        "partner_id": partner.id,
                        "account_id": debit_account.id,
                        "debit": amount_company,
                        "credit": 0.0,
                    }),
                    (0, 0, {
                        "name": rec.name,
                        "partner_id": partner.id,
                        "account_id": credit_account.id,
                        "debit": 0.0,
                        "credit": amount_company,
                    }),
                ],
            })
            move.action_post()

            rec.move_pdc_id = move
            rec._reconcile_with_invoices()
            rec.state = "registered"

    def action_collect(self):
        for rec in self:
            if rec.state != "registered":
                raise UserError(_("Only Registered PDCs can be collected."))

            pdc_account, _bounce, _reg_journal, bank_journal, _origin_type = rec._get_pdc_accounts_and_journals()

            company = rec.company_id
            partner = rec.partner_id.commercial_partner_id

            amount_company = rec.amount
            if rec.currency_id != company.currency_id:
                amount_company = rec.currency_id._convert(rec.amount, company.currency_id, company, rec.cheque_date)

            # Customer: Dr Bank / Cr PDC
            # Vendor:   Dr PDC  / Cr Bank
            if rec.pdc_type == "customer":
                debit_account = bank_journal.default_account_id
                credit_account = pdc_account
            else:
                debit_account = pdc_account
                credit_account = bank_journal.default_account_id

            move = self.env["account.move"].create({
                "move_type": "entry",
                "date": rec.cheque_date,
                "ref": _("PDC Collection %s") % rec.name,
                "journal_id": bank_journal.id,
                "company_id": company.id,
                "line_ids": [
                    (0, 0, {
                        "name": _("PDC Collection %s") % rec.name,
                        "partner_id": partner.id,
                        "account_id": debit_account.id,
                        "debit": amount_company,
                        "credit": 0.0,
                    }),
                    (0, 0, {
                        "name": _("PDC Collection %s") % rec.name,
                        "partner_id": partner.id,
                        "account_id": credit_account.id,
                        "debit": 0.0,
                        "credit": amount_company,
                    }),
                ],
            })
            move.action_post()

            rec.move_collection_id = move
            rec._reconcile_pdc_account(pdc_account)
            rec.state = "done"

    def _unreconcile_invoices(self):
        for rec in self:
            for inv in rec.invoice_ids:
                ar_lines = inv.line_ids.filtered(
                    lambda l: l.account_id.account_type in ('asset_receivable', 'liability_payable')
                              and l.reconciled
                )
                for line in ar_lines:
                    line.remove_move_reconcile()

    def action_bounce(self):
        for rec in self:
            if rec.state not in ("registered", "done"):
                raise UserError(_("Only Registered or Collected PDCs can be bounced."))

            pdc_account, bounce_account, reg_journal, bank_journal, origin_type = rec._get_pdc_accounts_and_journals()

            if not bounce_account:
                raise UserError(_("Please configure the PDC Bounce Account in Accounting Settings."))

            company = rec.company_id
            partner = rec.partner_id.commercial_partner_id

            amount_company = rec.amount
            if rec.currency_id != company.currency_id:
                amount_company = rec.currency_id._convert(
                    rec.amount, company.currency_id, company, rec.cheque_date or rec.date
                )

            # STEP A. If collected, reverse bank entry
            if rec.state == "done":
                reverse_move = self.env["account.move"].create({
                    "move_type": "entry",
                    "date": rec.cheque_date or rec.date,
                    "ref": _("PDC Bounce Bank Reversal %s") % rec.name,
                    "journal_id": bank_journal.id,
                    "company_id": company.id,
                    "line_ids": [
                        (0, 0, {
                            "name": _("PDC Bounce %s") % rec.name,
                            "partner_id": partner.id,
                            "account_id": (
                                rec.invoice_ids[0]
                                .line_ids
                                .filtered(lambda l: l.account_id.account_type == origin_type)[0]
                                .account_id.id
                            ),
                            "debit": amount_company,
                            "credit": 0.0,
                        }),
                        (0, 0, {
                            "name": _("PDC Bounce %s") % rec.name,
                            "partner_id": partner.id,
                            "account_id": bank_journal.default_account_id.id,
                            "debit": 0.0,
                            "credit": amount_company,
                        }),
                    ],
                })
                reverse_move.action_post()

            # STEP B. Unreconcile invoice
            rec._unreconcile_invoices()

            # STEP C. Bounce expense entry
            # STEP C. Bounce expense entry
            move = self.env["account.move"].create({
                "move_type": "entry",
                "date": rec.cheque_date or rec.date,
                "ref": _("PDC Bounce %s") % rec.name,
                "journal_id": reg_journal.id,
                "company_id": company.id,
                "line_ids": [
                    (0, 0, {
                        "name": _("PDC Bounce %s") % rec.name,
                        "partner_id": partner.id,
                        "account_id": bounce_account.id,  # Dr. PDC Bounce
                        "debit": amount_company,
                        "credit": 0.0,
                    }),
                    (0, 0, {
                        "name": _("PDC Bounce %s") % rec.name,
                        "partner_id": partner.id,
                        "account_id": pdc_account.id,  # ✅ Cr. Customer PDC (was AR account)
                        "debit": 0.0,
                        "credit": amount_company,
                    }),
                ],
            })
            move.action_post()

            rec.move_bounce_id = move
            rec.state = "bounce"

    def action_cancel(self):
        for rec in self:
            if rec.state == "done":
                raise UserError(_("You cannot cancel a Collected PDC."))
            rec.state = "cancel"

    def action_reset_to_draft(self):
        for rec in self:
            if rec.state not in ("cancel", "bounce"):
                raise UserError(_("Reset to Draft is allowed only from Cancelled or Bounced."))
            rec.state = "draft"
