# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, models


def _vals(env, model, docids):
    docs = env[model].browse(docids)
    doc = docs[:1]
    if not doc:
        return {
            "docs": docs,
            "doc_title": "",
            "filter_summary": "",
            "column_labels": [],
            "row_values": [],
        }
    ctx = doc._get_pdf_render_context()
    return {"docs": docs, **ctx}


class ReportLeaveLedgerPdf(models.AbstractModel):
    _name = "report.IndiaHrReports.leave_pdf_report_ledger"
    _description = "Leave ledger PDF (company layout)"

    @api.model
    def _get_report_values(self, docids, data=None):
        return _vals(self.env, "hr.in.report.wizard.leave.ledger", docids)


class ReportLeaveBalancePdf(models.AbstractModel):
    _name = "report.IndiaHrReports.leave_pdf_report_balance"
    _description = "Leave balance PDF (company layout)"

    @api.model
    def _get_report_values(self, docids, data=None):
        return _vals(self.env, "hr.in.report.wizard.leave.balance", docids)


class ReportLeaveAccrualPdf(models.AbstractModel):
    _name = "report.IndiaHrReports.leave_pdf_report_accrual"
    _description = "Leave accrual audit PDF (company layout)"

    @api.model
    def _get_report_values(self, docids, data=None):
        return _vals(self.env, "hr.in.report.wizard.leave.accrual", docids)
