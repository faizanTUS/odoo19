# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
import base64
from collections import defaultdict
from io import BytesIO

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class PendingPaymentReportWizard(models.TransientModel):
    _name = "pending.payment.report.wizard"
    _description = "Pending Payment Report Wizard"

    # Many2many partner selection with dynamic label per invoice type (each needs its own relation table)
    partner_customer_ids = fields.Many2many(
        "res.partner",
        "pending_payment_report_wizard_customer_rel",
        "wizard_id",
        "partner_id",
        string="Customer",
        help="Leave empty for all customers. Select one or more customers.",
        domain=[("customer_rank", ">", 0)],
    )
    partner_vendor_ids = fields.Many2many(
        "res.partner",
        "pending_payment_report_wizard_vendor_rel",
        "wizard_id",
        "partner_id",
        string="Vendor",
        help="Leave empty for all vendors. Select one or more vendors.",
        domain=[("supplier_rank", ">", 0)],
    )
    partner_ids = fields.Many2many(
        "res.partner",
        "pending_payment_report_wizard_partner_rel",
        "wizard_id",
        "partner_id",
        string="Customer / Vendor",
        help="Leave empty for all. Select one or more customers/vendors.",
        domain=["|", ("customer_rank", ">", 0), ("supplier_rank", ">", 0)],
    )
    date_from = fields.Date(string="Start Date", help="Invoice/Bill date from (optional).")
    date_to = fields.Date(string="End Date", help="Invoice/Bill date to (optional).")
    due_date_from = fields.Date(string="Due Date From", required=True)
    due_date_to = fields.Date(string="Due Date To", required=True)
    currency_id = fields.Many2one("res.currency", string="Currency")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    user_id = fields.Many2one("res.users", string="Sale Person")
    invoice_type = fields.Selection(
        [
            ("out_invoice", "Customer Invoices Only"),
            ("in_invoice", "Vendor Bills Only"),
            ("both", "Both Invoices and Bills"),
        ],
        string="Invoice Type",
        default="out_invoice",
        required=True,
    )
    # Backward compatibility: old/cached client views may still request partner_id on read
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner (legacy)",
        compute="_compute_partner_id",
        store=False,
        readonly=True,
    )
    line_ids = fields.One2many(
        "pending.payment.report.line",
        "report_id",
        string="Report Lines",
        readonly=True,
    )

    @api.constrains("due_date_from", "due_date_to", "date_from", "date_to")
    def _check_dates(self):
        for rec in self:
            if rec.due_date_from and rec.due_date_to and rec.due_date_from > rec.due_date_to:
                raise ValidationError("Due Date From must be earlier than Due Date To.")
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise ValidationError("Start Date must be earlier than End Date.")

    @api.depends("partner_customer_ids", "partner_vendor_ids", "partner_ids", "invoice_type")
    def _compute_partner_id(self):
        """Legacy: first selected partner for backward compatibility with cached client views."""
        for w in self:
            ids = w._get_selected_partner_ids()
            w.partner_id = ids[0] if ids else False

    def _get_selected_partner_ids(self):
        """Return selected partner IDs based on invoice_type: Customer, Vendor, or Both."""
        self.ensure_one()
        if self.invoice_type == "out_invoice" and self.partner_customer_ids:
            return self.partner_customer_ids.ids
        if self.invoice_type == "in_invoice" and self.partner_vendor_ids:
            return self.partner_vendor_ids.ids
        if self.invoice_type == "both" and self.partner_ids:
            return self.partner_ids.ids
        return []

    def _create_report_lines(self):
        """Create transient report line records. Call before opening tree or printing."""
        self.ensure_one()
        self.line_ids.unlink()
        Line = self.env["pending.payment.report.line"]
        Detail = self.env["pending.payment.report.line.detail"]
        move_ids_key = "move_ids"
        for row in self._get_report_data():
            moves = row.pop(move_ids_key, self.env["account.move"])
            row["report_id"] = self.id
            line = Line.create(row)
            for move in moves:
                Detail.create({"line_id": line.id, "move_id": move.id})
        return self.line_ids

    def _get_invoice_domain(self):
        self.ensure_one()
        if self.invoice_type == "both":
            move_types = ["out_invoice", "out_refund", "in_invoice", "in_refund"]
        elif self.invoice_type == "in_invoice":
            move_types = ["in_invoice", "in_refund"]
        else:
            move_types = ["out_invoice", "out_refund"]
        domain = [
            ("move_type", "in", move_types),
            ("state", "=", "posted"),
            ("payment_state", "in", ["not_paid", "partial"]),
            ("invoice_date_due", ">=", self.due_date_from),
            ("invoice_date_due", "<=", self.due_date_to),
            ("company_id", "=", self.company_id.id),
        ]
        if self.date_from:
            domain.append(("invoice_date", ">=", self.date_from))
        if self.date_to:
            domain.append(("invoice_date", "<=", self.date_to))
        partner_ids = self._get_selected_partner_ids()
        if partner_ids:
            domain.append(("partner_id", "in", partner_ids))
        if self.currency_id:
            domain.append(("currency_id", "=", self.currency_id.id))
        if self.user_id:
            domain.append(("invoice_user_id", "=", self.user_id.id))
        return domain

    def _get_no_data_message(self):
        """Helpful error when no moves match: show selected due date range and hint."""
        self.ensure_one()
        return (
            "No pending payment data found for the selected filters.\n\n"
            "Your filters: Due Date From = %s, Due Date To = %s, Invoice Type = %s.\n\n"
            "The report only includes POSTED customer invoices or vendor bills that are "
            "NOT fully paid (Not Paid or Partial) and whose DUE DATE is between Due Date From and Due Date To.\n\n"
            "If you have such invoices/bills but still see this message, check that their "
            "Due Date falls INSIDE the range above (e.g. if Due Date is 31/03/2026, set Due Date To to 31/03/2026 or later)."
        ) % (
            self.due_date_from,
            self.due_date_to,
            dict(self._fields["invoice_type"].selection).get(self.invoice_type, self.invoice_type),
        )

    def _get_report_data(self):
        """Build report lines aggregated by partner (and currency, and move_type when both)."""
        self.ensure_one()
        domain = self._get_invoice_domain()
        moves = self.env["account.move"].search(domain, order="partner_id, currency_id, move_type")
        if not moves:
            return []

        # When "both", group by (partner, currency, move_type); else (partner, currency)
        group_by_type = self.invoice_type == "both"
        groups = defaultdict(lambda: {"total": 0, "paid": 0, "pending": 0, "moves": self.env["account.move"]})
        for move in moves:
            mt = move.move_type in ("out_invoice", "out_refund") and "out_invoice" or "in_invoice"
            key = (move.partner_id.id, move.currency_id.id, mt) if group_by_type else (move.partner_id.id, move.currency_id.id)
            if not group_by_type:
                key = key + (None,)
            groups[key]["total"] += move.amount_total_signed
            groups[key]["paid"] += move.amount_total_signed - move.amount_residual_signed
            groups[key]["pending"] += move.amount_residual_signed
            groups[key]["moves"] |= move

        lines = []
        for key, vals in groups.items():
            partner_id, currency_id = key[0], key[1]
            move_type = key[2] if group_by_type else (self.invoice_type if self.invoice_type != "both" else None)
            lines.append(
                {
                    "partner_id": partner_id,
                    "currency_id": currency_id,
                    "move_type": move_type,
                    "total": vals["total"],
                    "paid_amount": vals["paid"],
                    "pending_amount": vals["pending"],
                    "invoice_count": len(vals["moves"]),
                    "move_ids": vals["moves"],
                }
            )
        return lines

    def action_view_report(self):
        """Create lines and open tree view."""
        self.ensure_one()
        lines = self._create_report_lines()
        if not lines:
            raise UserError(self._get_no_data_message())
        return {
            "name": "Pending Payment Report",
            "type": "ir.actions.act_window",
            "res_model": "pending.payment.report.line",
            "view_mode": "tree",
            "views": [(self.env.ref("pending_payment_report.view_pending_payment_report_line_tree").id, "tree")],
            "domain": [("report_id", "=", self.id)],
            "context": {"create": False, "edit": False},
        }

    def action_print_report(self):
        """Print PDF report."""
        self.ensure_one()
        lines = self._create_report_lines()
        if not lines:
            raise UserError(self._get_no_data_message())
        return self.env.ref("pending_payment_report.action_report_pending_payment").report_action(self)

    def _build_excel_data(self):
        """Build Excel content: data rows + currency totals + grand total. Returns (header_cols, data_rows, currency_totals, grand_total)."""
        self.ensure_one()
        has_type = self.invoice_type == "both"
        # Header
        header = ["Customer / Vendor"]
        if has_type:
            header.append("Type")
        header += ["Currency", "Total", "Received Amount", "Payment Date(s)", "Pending Amount", "Invoice Count", "Email ID"]
        # Data rows (grouped by customer/vendor)
        data_rows = []
        for line in self.line_ids:
            payment_dates = ""
            if line.detail_ids:
                dates_set = set()
                for d in line.detail_ids:
                    if d.payment_dates:
                        dates_set.update(d.payment_dates.replace(" ", "").split(","))
                payment_dates = ", ".join(sorted(dates_set)) if dates_set else ""
            type_label = ""
            if line.move_type:
                type_label = "Customer Invoice" if line.move_type == "out_invoice" else "Vendor Bill"
            row = [line.partner_id.display_name or ""]
            if has_type:
                row.append(type_label)
            row += [
                line.currency_id.name if line.currency_id else "",
                line.total or 0,
                line.paid_amount or 0,
                payment_dates,
                line.pending_amount or 0,
                line.invoice_count or 0,
                line.email_id or "",
            ]
            data_rows.append(row)
        # Currency wise totals
        currency_sums = {}
        for line in self.line_ids:
            ckey = (line.currency_id.id if line.currency_id else 0, line.currency_id.name if line.currency_id else "")
            if ckey not in currency_sums:
                currency_sums[ckey] = {"total": 0, "paid": 0, "pending": 0, "count": 0}
            currency_sums[ckey]["total"] += line.total or 0
            currency_sums[ckey]["paid"] += line.paid_amount or 0
            currency_sums[ckey]["pending"] += line.pending_amount or 0
            currency_sums[ckey]["count"] += line.invoice_count or 0
        currency_rows = []
        for (_cid, cname), vals in sorted(currency_sums.items(), key=lambda x: (x[0][1] or "ZZZ")):
            r = ["Total (%s)" % (cname or "?")]
            if has_type:
                r.append("")
            r += [cname or "", vals["total"], vals["paid"], "", vals["pending"], vals["count"], ""]
            currency_rows.append(r)
        grand = {
            "total": sum(s["total"] for s in currency_sums.values()),
            "paid": sum(s["paid"] for s in currency_sums.values()),
            "pending": sum(s["pending"] for s in currency_sums.values()),
            "count": sum(s["count"] for s in currency_sums.values()),
        }
        grand_row = ["Grand Total"]
        if has_type:
            grand_row.append("")
        grand_row += ["", grand["total"], grand["paid"], "", grand["pending"], grand["count"], ""]
        return header, data_rows, currency_rows, grand_row

    def _build_excel_sheet_customers(self):
        """Build customer sheet rows: grouped by customer, detail lines with Sr.No, Invoice No, Invoice DT, Due Date, Invoice Amount, Received Amount, Payment Date, Currency, Due Amount, Due in Co Currency."""
        self.ensure_one()
        lines = [l for l in self.line_ids if l.move_type in (False, "out_invoice")]
        header = ["Sr.No", "Invoice No", "Invoice DT", "Due Date", "Invoice Amount", "Received Amount", "Payment Date(s)", "Invoice Currency", "Due Amount", "Due Amount in Company Currency"]
        all_rows = []
        grand_inv_amt = grand_paid = grand_due = grand_due_cc = 0
        for line in lines:
            all_rows.append([f"Customer: {line.partner_id.display_name or ''}"])
            sr = 0
            cust_inv_amt = cust_paid = cust_due = cust_due_cc = 0
            for d in line.detail_ids:
                sr += 1
                inv_amt = d.amount_total or 0
                paid = d.received_amount or 0
                due = d.amount_residual or 0
                due_cc = getattr(d, "amount_residual_signed", 0) or 0
                cust_inv_amt += inv_amt
                cust_paid += paid
                cust_due += due
                cust_due_cc += due_cc
                grand_inv_amt += inv_amt
                grand_paid += paid
                grand_due += due
                grand_due_cc += due_cc
                curr_name = (d.currency_id and d.currency_id.symbol) or (d.move_id.currency_id.symbol if d.move_id else "")
                all_rows.append([
                    sr,
                    d.invoice_number or "",
                    d.invoice_date or "",
                    d.due_date or "",
                    inv_amt,
                    paid,
                    d.payment_dates or "",
                    curr_name,
                    due,
                    due_cc,
                ])
            all_rows.append(["Total", "", "", "", cust_inv_amt, cust_paid, "", "", cust_due, cust_due_cc])
            all_rows.append([])
        all_rows.append(["GRAND TOTAL", "", "", "", grand_inv_amt, grand_paid, "", "", grand_due, grand_due_cc])
        return "Pending Payment from Customers", header, all_rows

    def _build_excel_sheet_vendors(self):
        """Build vendor sheet rows: grouped by vendor, detail lines with No, Vendor Bill no, Bill Dt, Due Dt, Bill Amount, Payment Info., Paid Amount, Due Amount, Bill Currency, Due in Co Currency."""
        self.ensure_one()
        lines = [l for l in self.line_ids if l.move_type in (False, "in_invoice")]
        header = ["No", "Vendor Bill no", "Bill Dt", "Due Dt", "Bill Amount", "Payment Info.", "Paid Amount", "Due Amount", "Bill Currency", "Due Amount in Company Currency"]
        all_rows = []
        grand_inv_amt = grand_paid = grand_due = grand_due_cc = 0
        for line in lines:
            all_rows.append([f"Vendor: {line.partner_id.display_name or ''}"])
            sr = 0
            vend_inv_amt = vend_paid = vend_due = vend_due_cc = 0
            for d in line.detail_ids:
                sr += 1
                inv_amt = d.amount_total or 0
                paid = d.received_amount or 0
                due = d.amount_residual or 0
                due_cc = getattr(d, "amount_residual_signed", 0) or 0
                vend_inv_amt += inv_amt
                vend_paid += paid
                vend_due += due
                vend_due_cc += due_cc
                grand_inv_amt += inv_amt
                grand_paid += paid
                grand_due += due
                grand_due_cc += due_cc
                curr_name = (d.currency_id and d.currency_id.symbol) or (d.move_id.currency_id.symbol if d.move_id else "")
                payment_info = (d.payment_dates and f"{paid} paid on {d.payment_dates}" or str(paid))
                all_rows.append([
                    sr,
                    d.invoice_number or "",
                    d.invoice_date or "",
                    d.due_date or "",
                    inv_amt,
                    payment_info,
                    paid,
                    due,
                    curr_name,
                    due_cc,
                ])
            all_rows.append(["Total", "", "", "", vend_inv_amt, "", vend_paid, vend_due, "", vend_due_cc])
            all_rows.append([])
        all_rows.append(["GRAND TOTAL", "", "", "", grand_inv_amt, "", grand_paid, grand_due, "", grand_due_cc])
        return "Bill Payment Pending Report", header, all_rows

    def _write_excel_to_buffer(self):
        """Write 1 or 2 sheets to workbook buffer; returns bytes. Assumes line_ids already created."""
        self.ensure_one()
        import xlsxwriter
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        bold = workbook.add_format({"bold": True})
        num_fmt = workbook.add_format({"num_format": "#,##0.00"})
        date_fmt = workbook.add_format({"num_format": "yyyy-mm-dd"})

        def write_sheet(sheet_name, header, all_rows):
            sheet = workbook.add_worksheet(sheet_name[:31])
            r = 0
            for col, label in enumerate(header):
                sheet.write(r, col, label, bold)
            r += 1
            for row_data in all_rows:
                if not row_data:
                    r += 1
                    continue
                is_bold = False
                if len(row_data) == 1 and isinstance(row_data[0], str):
                    is_bold = True
                if isinstance(row_data[0], str) and ("Customer:" in row_data[0] or "Vendor:" in row_data[0] or "Total" in row_data[0] or "GRAND" in row_data[0]):
                    is_bold = True
                for col, val in enumerate(row_data):
                    if isinstance(val, (int, float)) and not isinstance(val, bool):
                        sheet.write(r, col, val, num_fmt)
                    elif hasattr(val, "strftime"):
                        sheet.write(r, col, val, date_fmt)
                    else:
                        sheet.write(r, col, val, bold if is_bold else None)
                r += 1
            for c in range(len(header)):
                sheet.set_column(c, c, 16 if c > 0 else 36)
            return sheet

        if self.invoice_type == "both":
            # Sheet 1: Pending Payment from Customers
            cust_title, cust_header, cust_rows = self._build_excel_sheet_customers()
            if cust_rows:
                write_sheet(cust_title, cust_header, cust_rows)
            # Sheet 2: Bill Payment Pending Report
            vend_title, vend_header, vend_rows = self._build_excel_sheet_vendors()
            if vend_rows:
                write_sheet(vend_title, vend_header, vend_rows)
        elif self.invoice_type == "out_invoice":
            cust_title, cust_header, cust_rows = self._build_excel_sheet_customers()
            write_sheet(cust_title, cust_header, cust_rows)
        else:
            vend_title, vend_header, vend_rows = self._build_excel_sheet_vendors()
            write_sheet(vend_title, vend_header, vend_rows)

        workbook.close()
        output.seek(0)
        return output.read()

    def _get_excel_bytes(self):
        """Generate Excel file bytes (1 or 2 sheets). Call after _create_report_lines()."""
        self.ensure_one()
        try:
            import xlsxwriter
        except ImportError:
            raise UserError("Please install the 'xlsxwriter' Python package to export Excel.")
        return self._write_excel_to_buffer()

    def action_print_excel(self):
        """Export to Excel: 1 sheet (Customers or Vendors) or 2 sheets (Customers + Vendors) when Both."""
        self.ensure_one()
        self._create_report_lines()
        if not self.line_ids:
            raise UserError(self._get_no_data_message())
        excel_bytes = self._get_excel_bytes()
        filename = "Pending_Payment_Report.xlsx"
        attachment = self.env["ir.attachment"].create(
            {
                "name": filename,
                "type": "binary",
                "datas": base64.b64encode(excel_bytes),
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

    def _get_configured_recipient(self):
        partner_id = self.env["ir.config_parameter"].sudo().get_param("pending_payment_report.recipient_id")
        if not partner_id:
            return self.env["res.partner"]
        return self.env["res.partner"].browse(int(partner_id)).exists()

    def action_send_to_configured_user(self):
        """Generate Excel report and send it by email to the configured user (Settings)."""
        self.ensure_one()
        recipient = self._get_configured_recipient()
        if not recipient or not recipient.email:
            raise UserError(
                "No recipient configured for auto-send. Go to Invoicing → Configuration → Pending Payment Report Settings "
                "and set 'Auto-send Pending Payment Report To'."
            )
        self._create_report_lines()
        if not self.line_ids:
            raise UserError(self._get_no_data_message())
        excel_bytes = self._get_excel_bytes()
        filename = "Pending_Payment_Report.xlsx"
        attachment = self.env["ir.attachment"].create(
            {
                "name": filename,
                "type": "binary",
                "datas": base64.b64encode(excel_bytes),
                "res_model": self._name,
                "res_id": self.id,
                "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
        )
        template = self.env.ref(
            "pending_payment_report.mail_template_pending_payment_report_to_user",
            raise_if_not_found=False,
        )
        subject = f"Pending Payment Report - {self.due_date_from} to {self.due_date_to}"
        body = f"Please find attached the Pending Payment Report (Due: {self.due_date_from} to {self.due_date_to})."
        if template:
            subj_dict = template._render_field("subject", self.ids, compute_lang=True)
            body_dict = template._render_field("body_html", self.ids, compute_lang=True)
            if subj_dict:
                subject = subj_dict.get(self.id, subject)
            if body_dict:
                body = body_dict.get(self.id, body)
        mail = self.env["mail.mail"].create(
            {
                "subject": subject,
                "body_html": body,
                "email_to": recipient.email,
                "attachment_ids": [(4, attachment.id)],
                "author_id": self.env.user.partner_id.id,
            }
        )
        mail.send()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Email Sent",
                "message": f"Pending Payment Report has been sent to {recipient.email}.",
                "type": "success",
                "sticky": False,
            },
        }
