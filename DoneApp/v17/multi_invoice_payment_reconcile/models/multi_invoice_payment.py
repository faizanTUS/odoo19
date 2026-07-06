# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)

class MultiInvoicePaymentLine(models.TransientModel):
    _name = "multi.invoice.payment.line"
    _description = "Multi Invoice Payment Line"

    wizard_id = fields.Many2one(
        "multi.invoice.payment.wizard",
        required=True,
        ondelete="cascade",
    )

    invoice_id = fields.Many2one(
        "account.move",
        required=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        readonly=True,
    )

    residual = fields.Monetary(currency_field="currency_id", readonly=True)
    amount = fields.Monetary(currency_field="currency_id")

    invoice_date = fields.Date(related="invoice_id.invoice_date", readonly=True)
    invoice_date_due = fields.Date(related="invoice_id.invoice_date_due", readonly=True)
    name = fields.Char(related="invoice_id.name", readonly=True)
    move_type = fields.Selection(related="invoice_id.move_type", readonly=True)

    # XML-required helper fields
    invoice_number = fields.Char(related="invoice_id.name", readonly=True)
    currency_name = fields.Char(related="currency_id.name", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        clean_vals = []
        for vals in vals_list:
            if vals.get("invoice_id"):
                clean_vals.append(vals)
        return super().create(clean_vals)


class MultiInvoicePaymentWizard(models.TransientModel):
    _name = 'multi.invoice.payment.wizard'
    _description = 'Multi Invoice Payment Wizard'
    active = fields.Boolean(default=True)

    partner_type = fields.Selection(
        [("customer", "Customer"), ("supplier", "Vendor")],
        default="customer",
        required=True,
    )
    payment_type = fields.Selection(
        [("inbound", "Receive Money"), ("outbound", "Send Money")],
        default="inbound",
        required=True,
    )

    partner_id = fields.Many2one("res.partner", required=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )

    journal_id = fields.Many2one(
        "account.journal",
        required=True,
        domain="[('type','in',('bank','cash')),('company_id','=',company_id)]",
    )

    currency_id = fields.Many2one(
        "res.currency",
        readonly=True,
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    payment_date = fields.Date(
        default=fields.Date.context_today,
        required=True,
    )
    memo = fields.Char()

    line_ids = fields.One2many(
        "multi.invoice.payment.line",
        "wizard_id",
        string="Invoices / Bills",
        copy=False,
    )

    allocated_amount = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_amounts",
    )
    amount_total = fields.Monetary(currency_field="currency_id")
    extra_amount = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_amounts",
    )

    @api.onchange("partner_type")
    def _onchange_partner_type(self):
        for wiz in self:
            wiz.payment_type = "inbound" if wiz.partner_type == "customer" else "outbound"

    @api.onchange("payment_type")
    def _onchange_payment_type(self):
        for wiz in self:
            wiz.partner_type = "customer" if wiz.payment_type == "inbound" else "supplier"

    @api.onchange("partner_id", "payment_type", "company_id")
    def _onchange_partner_load_invoices(self):
        for wiz in self:
            wiz.line_ids = [(5, 0, 0)]
            wiz.amount_total = 0.0

            if not wiz.partner_id:
                return

            domain = [
                ("state", "=", "posted"),
                ("company_id", "=", wiz.company_id.id),
                ("partner_id", "=", wiz.partner_id.id),
                ("amount_residual", ">", 0),
            ]

            if wiz.payment_type == "inbound":
                domain.append(("move_type", "in", ("out_invoice", "out_refund")))
            else:
                domain.append(("move_type", "in", ("in_invoice", "in_refund")))

            moves = self.env["account.move"].search(domain, order="invoice_date_due asc")

            if not moves:
                return

            currencies = moves.mapped("currency_id")
            if len(currencies) > 1:
                raise UserError(_("Partner has open documents in multiple currencies."))

            wiz.currency_id = currencies[0]

            lines = []
            for mv in moves:
                lines.append((0, 0, {
                    "invoice_id": mv.id,
                    "currency_id": wiz.currency_id.id,
                    "residual": mv.amount_residual,
                    "amount": mv.amount_residual,
                }))

            wiz.line_ids = lines
            wiz.amount_total = sum(m.amount_residual for m in moves)

    @api.depends("line_ids.amount", "amount_total")
    def _compute_amounts(self):
        for wiz in self:
            allocated = sum(wiz.line_ids.mapped("amount"))
            wiz.allocated_amount = allocated
            wiz.extra_amount = (wiz.amount_total or 0.0) - allocated

    def action_confirm(self):
        # print("\n\n self line", self.line_ids)
        self._onchange_partner_load_invoices()
        valid_lines = self.line_ids.filtered(
            lambda l: l.invoice_id and float_compare(
                l.amount or 0.0,
                0.0,
                precision_rounding=self.currency_id.rounding
            ) > 0
        )
        # print("\n\n valid line", valid_lines)
        if float_compare(
                self.amount_total or 0.0,
                0.0,
                precision_rounding=self.currency_id.rounding
        ) <= 0:
            raise UserError(_("Payment Amount must be greater than zero."))
        for line in valid_lines:
            # print("\n\n line", line)
            if float_compare(
                    line.amount,
                    (line.invoice_id.amount_residual),
                    precision_rounding=line.currency_id.rounding
            ) > 0:
                raise UserError(
                    _("You cannot allocate more than residual for %s.")
                    % line.invoice_id.display_name
                )
        pml = (
            self.journal_id.inbound_payment_method_line_ids[:1]
            if self.payment_type == "inbound"
            else self.journal_id.outbound_payment_method_line_ids[:1]
        )
        if not pml:
            raise UserError(_("No payment method line found on selected journal."))

        payment = self.env["account.payment"].create({
            "payment_type": self.payment_type,
            "partner_type": self.partner_type,
            "partner_id": self.partner_id.id,
            "amount": self.amount_total,
            "currency_id": self.currency_id.id,
            "journal_id": self.journal_id.id,
            "payment_method_line_id": pml.id,
            "date": self.payment_date,
            "ref": self.memo,
        })
        # move_vals = payment._generate_move_vals()
        # payment.move_id = self.env["account.move"].create(move_vals)
        # # print("\n\n payment.move_id", payment.move_id)
        # payment.move_id.action_post()
        # payment.action_validate()
        payment.action_post()
        account_type = (
            "asset_receivable"
            if self.payment_type == "inbound"
            else "liability_payable"
        )
        counterpart = payment.move_id.line_ids.filtered(
            lambda l: l.account_id.account_type == account_type and not l.reconciled
        )[:1]
        if not counterpart:
            raise UserError(_("Could not find counterpart line to reconcile."))
        Partial = self.env["account.partial.reconcile"]
        # print(" Partial", Partial)
        for line in valid_lines:
            # print("\n\n line---", line)

            inv_line = line.invoice_id.line_ids.filtered(
                lambda l: l.account_id.account_type == account_type and not l.reconciled
            )[:1]
            # print("\n inv_line", inv_line)
            if not inv_line:
                continue
            debit_line, credit_line = (
                (inv_line, counterpart)
                if inv_line.balance > 0
                else (counterpart, inv_line)
            )
            Partial.create({
                "debit_move_id": debit_line.id if debit_line else False,
                "credit_move_id": credit_line.id if credit_line else False,
                'debit_amount_currency': debit_line.amount_currency if debit_line else False,
                'credit_amount_currency': credit_line.amount_currency if credit_line else False,
                "amount": abs(line.amount),
            })
            # print("\n Partial ----", Partial)
        self.env.flush_all()
        payment._compute_reconciliation_status()