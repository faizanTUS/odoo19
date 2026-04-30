# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
import csv
import io

from odoo import http
from odoo.http import content_disposition, request


class PettyCashReportController(http.Controller):
    @http.route("/petty_cash/aging_report_csv", type="http", auth="user")
    def aging_report_csv(self, **kwargs):
        """Excel-friendly CSV export of aging lines (same domain as list view)."""
        ids = kwargs.get("ids")
        if not ids:
            return request.not_found()
        id_list = [int(x) for x in ids.split(",") if x.isdigit()]
        vouchers = request.env["petty.cash.voucher"].search([("id", "in", id_list)])
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            [
                "Reference",
                "Fund",
                "Employee",
                "Date",
                "Amount",
                "Status",
                "Days Pending",
                "Aging Bucket",
            ]
        )
        for v in vouchers:
            writer.writerow(
                [
                    v.name,
                    v.fund_id.name or "",
                    v.employee_id.name or "",
                    v.date.isoformat() if v.date else "",
                    v.amount,
                    v.state,
                    v.days_pending,
                    dict(v._fields["aging_bucket"].selection).get(v.aging_bucket, ""),
                ]
            )
        data = buffer.getvalue().encode("utf-8-sig")
        filename = "petty_cash_aging_report.csv"
        headers = [
            ("Content-Type", "text/csv; charset=utf-8"),
            ("Content-Disposition", content_disposition(filename)),
        ]
        return request.make_response(data, headers)
