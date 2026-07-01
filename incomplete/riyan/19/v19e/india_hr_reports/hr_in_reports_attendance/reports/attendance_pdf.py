# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, models


def _vals(env, wizard_model, docids):
    docs = env[wizard_model].browse(docids)
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


class ReportAttDailyPdf(models.AbstractModel):
    _name = "report.india_hr_reports.att_pdf_daily_document"
    _description = "PDF daily attendance (professional layout)"

    @api.model
    def _get_report_values(self, docids, data=None):
        return _vals(self.env, "hr.in.report.wizard.att.daily", docids)


class ReportAttMonthlyPdf(models.AbstractModel):
    _name = "report.india_hr_reports.att_pdf_monthly_document"
    _description = "PDF attendance matrix (professional layout)"

    @api.model
    def _get_report_values(self, docids, data=None):
        return _vals(self.env, "hr.in.report.wizard.att.monthly", docids)


class ReportAttExceptionsPdf(models.AbstractModel):
    _name = "report.india_hr_reports.att_pdf_exceptions_document"
    _description = "PDF attendance exceptions (professional layout)"

    @api.model
    def _get_report_values(self, docids, data=None):
        return _vals(self.env, "hr.in.report.wizard.att.exceptions", docids)


class ReportAttOtPdf(models.AbstractModel):
    _name = "report.india_hr_reports.att_pdf_ot_document"
    _description = "PDF overtime summary (professional layout)"

    @api.model
    def _get_report_values(self, docids, data=None):
        return _vals(self.env, "hr.in.report.wizard.att.ot", docids)
