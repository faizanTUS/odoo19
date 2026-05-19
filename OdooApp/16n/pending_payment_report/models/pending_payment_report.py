# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from datetime import date

from odoo import api, fields, models


class PendingPaymentReportLine(models.TransientModel):
    _name = "pending.payment.report.line"
    _description = "Pending Payment Report Line"

    report_id = fields.Many2one(
        "pending.payment.report.wizard",
        string="Report",
        ondelete="cascade",
    )
    partner_id = fields.Many2one("res.partner", string="Customer / Vendor", required=True)
    move_type = fields.Selection(
        [
            ("out_invoice", "Customer Invoice"),
            ("in_invoice", "Vendor Bill"),
        ],
        string="Type",
        help="Invoice or Bill when report includes both.",
    )
    currency_id = fields.Many2one("res.currency", string="Currency")
    total = fields.Monetary(string="Total", currency_field="currency_id")
    paid_amount = fields.Monetary(string="Paid Amount", currency_field="currency_id")
    pending_amount = fields.Monetary(string="Pending Amount", currency_field="currency_id")
    invoice_count = fields.Integer(string="Invoice Count", default=0)
    email = fields.Boolean(string="Email", default=False)
    email_id = fields.Char(string="Email ID", related="partner_id.email", readonly=True)
    detail_ids = fields.One2many(
        "pending.payment.report.line.detail",
        "line_id",
        string="Invoice Details",
    )

    def action_send_email(self):
        """Open email composer for selected report lines. Called from tree view."""
        if not self:
            return
        from odoo.exceptions import UserError
        template = self.env.ref(
            "pending_payment_report.mail_template_pending_payment_details",
            raise_if_not_found=False,
        )
        if not template:
            raise UserError("Email template 'Pending Payment Details' not found.")
        partners = self.mapped("partner_id").filtered(lambda p: p.email)
        if not partners:
            raise UserError("Selected customers have no email address set.")
        compose = self.env["mail.compose.message"].create(
            {
                "model": "pending.payment.report.line",
                "composition_mode": "mass_mail",
                "template_id": template.id,
                "res_ids": self.ids,
                "partner_ids": [(6, 0, partners.ids)],
            }
        )
        compose._compute_body()
        compose._compute_subject()
        return {
            "name": "Send Pending Payment Details",
            "type": "ir.actions.act_window",
            "res_model": "mail.compose.message",
            "view_mode": "form",
            "res_id": compose.id,
            "target": "new",
            "context": dict(
                self.env.context,
                default_model="pending.payment.report.line",
                default_template_id=template.id,
                active_ids=self.ids,
            ),
        }


class PendingPaymentReportLineDetail(models.TransientModel):
    _name = "pending.payment.report.line.detail"
    _description = "Pending Payment Report Line Detail (per invoice)"

    line_id = fields.Many2one(
        "pending.payment.report.line",
        string="Report Line",
        ondelete="cascade",
    )
    move_id = fields.Many2one("account.move", string="Invoice")
    invoice_number = fields.Char(related="move_id.name", string="Invoice Number", readonly=True)
    due_date = fields.Date(related="move_id.invoice_date_due", string="Due Date", readonly=True)
    overdue_days = fields.Integer(string="Overdue Days", compute="_compute_overdue_days", store=False)
    amount_total = fields.Monetary(
        related="move_id.amount_total",
        string="Total",
        currency_field="currency_id",
        readonly=True,
    )
    amount_residual = fields.Monetary(
        related="move_id.amount_residual",
        string="Pending",
        currency_field="currency_id",
        readonly=True,
    )
    amount_residual_signed = fields.Monetary(
        related="move_id.amount_residual_signed",
        string="Due in Company Currency",
        currency_field="company_currency_id",
        readonly=True,
    )
    company_currency_id = fields.Many2one(related="move_id.company_currency_id", readonly=True)
    invoice_date = fields.Date(related="move_id.invoice_date", string="Invoice Date", readonly=True)
    received_amount = fields.Monetary(
        string="Received Amount",
        compute="_compute_received_amount",
        currency_field="currency_id",
        readonly=True,
    )
    payment_dates = fields.Char(
        string="Payment Date(s)",
        compute="_compute_payment_dates",
        readonly=True,
    )
    currency_id = fields.Many2one(related="move_id.currency_id", readonly=True)

    @api.depends("move_id", "move_id.amount_total", "move_id.amount_residual")
    def _compute_received_amount(self):
        for rec in self:
            if rec.move_id:
                rec.received_amount = (rec.move_id.amount_total or 0) - (rec.move_id.amount_residual or 0)
            else:
                rec.received_amount = 0

    @api.depends("move_id.line_ids.matched_debit_ids", "move_id.line_ids.matched_credit_ids")
    def _compute_payment_dates(self):
        for rec in self:
            payments = rec.move_id._get_reconciled_payments() if rec.move_id else False
            dates = payments.mapped("date") if payments else []
            rec.payment_dates = ", ".join(sorted(map(str, dates))) if dates else ""

    def _compute_overdue_days(self):
        today = date.today()
        for rec in self:
            if rec.due_date and rec.due_date < today:
                rec.overdue_days = (today - rec.due_date).days
            else:
                rec.overdue_days = 0
