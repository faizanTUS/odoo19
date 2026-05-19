# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
import base64
from collections import defaultdict
from io import BytesIO

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class AdvancePendingPaymentReportWizard(models.TransientModel):
    _name = "advance.pending.payment.report.wizard"
    _description = "Advance Pending Payment Report Wizard"

    partner_id = fields.Many2one("res.partner", string="Partner")
    date_from = fields.Date(string="From Date", required=True)
    date_to = fields.Date(string="To Date", required=True)
    user_id = fields.Many2one("res.users", string="Sale Person")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    invoice_type = fields.Selection(
        [
            ("out_invoice", "Customer Invoices"),
            ("in_invoice", "Vendor Bills"),
        ],
        string="Invoice Type",
        default="out_invoice",
        required=True,
    )
    line_ids = fields.One2many(
        "advance.pending.payment.report.line",
        "report_id",
        string="Report Lines",
        readonly=True,
    )

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise ValidationError("From Date must be earlier than To Date.")

    def _get_invoice_domain(self):
        self.ensure_one()
        move_types = (
            ["out_invoice", "out_refund"] if self.invoice_type == "out_invoice" else ["in_invoice", "in_refund"]
        )
        domain = [
            ("move_type", "in", move_types),
            ("state", "=", "posted"),
            ("payment_state", "in", ["not_paid", "partial"]),
            ("invoice_date_due", ">=", self.date_from),
            ("invoice_date_due", "<=", self.date_to),
            ("company_id", "=", self.company_id.id),
        ]
        if self.partner_id:
            domain.append(("partner_id", "=", self.partner_id.id))
        if self.user_id:
            domain.append(("invoice_user_id", "=", self.user_id.id))
        return domain

    def _get_report_data(self):
        self.ensure_one()
        domain = self._get_invoice_domain()
        moves = self.env["account.move"].search(domain, order="partner_id, currency_id")
        if not moves:
            return []

        groups = defaultdict(lambda: {"total": 0, "paid": 0, "pending": 0, "moves": self.env["account.move"]})
        for move in moves:
            key = (move.partner_id.id, move.currency_id.id)
            groups[key]["total"] += move.amount_total_signed
            groups[key]["paid"] += move.amount_total_signed - move.amount_residual_signed
            groups[key]["pending"] += move.amount_residual_signed
            groups[key]["moves"] |= move

        lines = []
        for (partner_id, currency_id), vals in groups.items():
            lines.append(
                {
                    "partner_id": partner_id,
                    "currency_id": currency_id,
                    "total": vals["total"],
                    "paid_amount": vals["paid"],
                    "pending_amount": vals["pending"],
                    "invoice_count": len(vals["moves"]),
                    "move_ids": vals["moves"],
                }
            )
        return lines

    def _create_report_lines(self):
        self.ensure_one()
        self.line_ids.unlink()
        Line = self.env["advance.pending.payment.report.line"]
        for row in self._get_report_data():
            row.pop("move_ids", None)
            row["report_id"] = self.id
            Line.create(row)
        return self.line_ids

    def action_view_report(self):
        self.ensure_one()
        lines = self._create_report_lines()
        if not lines:
            raise UserError("No pending payment data found for the selected filters.")
        return {
            "name": "Advance Pending Payment Report",
            "type": "ir.actions.act_window",
            "res_model": "advance.pending.payment.report.line",
            "view_mode": "tree",
            "views": [(self.env.ref("pending_payment_report.view_advance_pending_payment_report_line_tree").id, "tree")],
            "domain": [("report_id", "=", self.id)],
            "context": {"create": False, "edit": False},
        }

    def action_print_report(self):
        self.ensure_one()
        lines = self._create_report_lines()
        if not lines:
            raise UserError("No pending payment data found for the selected filters.")
        return self.env.ref("pending_payment_report.action_report_advance_pending_payment").report_action(self)

    def action_print_excel(self):
        self.ensure_one()
        lines = self._create_report_lines()
        if not lines:
            raise UserError("No pending payment data found for the selected filters.")
        try:
            import xlsxwriter
        except ImportError:
            raise UserError("Please install the 'xlsxwriter' Python package to export Excel.")
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        sheet = workbook.add_worksheet("Advance Pending Payment Report")
        bold = workbook.add_format({"bold": True})
        num_fmt = workbook.add_format({"num_format": "#,##0.00"})
        row = 0
        sheet.write(row, 0, "Partner", bold)
        sheet.write(row, 1, "Total", bold)
        sheet.write(row, 2, "Paid Amount", bold)
        sheet.write(row, 3, "Pending Amount", bold)
        sheet.write(row, 4, "Invoice Count", bold)
        sheet.write(row, 5, "Email ID", bold)
        row += 1
        grand_total = grand_paid = grand_pending = 0
        for line in self.line_ids:
            sheet.write(row, 0, line.partner_id.display_name or "")
            sheet.write(row, 1, line.total or 0, num_fmt)
            sheet.write(row, 2, line.paid_amount or 0, num_fmt)
            sheet.write(row, 3, line.pending_amount or 0, num_fmt)
            sheet.write(row, 4, line.invoice_count or 0)
            sheet.write(row, 5, line.email_id or "")
            grand_total += line.total or 0
            grand_paid += line.paid_amount or 0
            grand_pending += line.pending_amount or 0
            row += 1
        sheet.write(row, 0, "Grand Total", bold)
        sheet.write(row, 1, grand_total, num_fmt)
        sheet.write(row, 2, grand_paid, num_fmt)
        sheet.write(row, 3, grand_pending, num_fmt)
        sheet.write(row, 4, sum(self.line_ids.mapped("invoice_count")), bold)
        sheet.set_column(0, 0, 40)
        sheet.set_column(1, 5, 16)
        workbook.close()
        output.seek(0)
        attachment = self.env["ir.attachment"].create(
            {
                "name": "Advance_Pending_Payment_Report.xlsx",
                "type": "binary",
                "datas": base64.b64encode(output.read()),
                "res_model": self._name,
                "res_id": self.id,
                "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
        )
        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "self",
        }
