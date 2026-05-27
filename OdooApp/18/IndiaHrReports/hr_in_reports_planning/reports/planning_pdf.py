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


class ReportPlanCoverage(models.AbstractModel):
    _name = "report.IndiaHrReports.pay_plan_coverage_document"
    _description = "PDF shift coverage"

    @api.model
    def _get_report_values(self, docids, data=None):
        return _vals(self.env, "hr.in.report.wizard.plan.coverage", docids)


class ReportPlanUnderOver(models.AbstractModel):
    _name = "report.IndiaHrReports.pay_plan_under_over_document"
    _description = "PDF under/over planning"

    @api.model
    def _get_report_values(self, docids, data=None):
        return _vals(self.env, "hr.in.report.wizard.plan.under_over", docids)
