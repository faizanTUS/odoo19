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


class ReportExpConsolidated(models.AbstractModel):
    _name = "report.india_hr_reports.exp_pdf_cons"
    _description = "PDF consolidated claims"

    @api.model
    def _get_report_values(self, docids, data=None):
        return _vals(self.env, "hr.in.report.wizard.exp.consolidated", docids)


class ReportExpProduct(models.AbstractModel):
    _name = "report.india_hr_reports.exp_pdf_prod"
    _description = "PDF product analytic claims"

    @api.model
    def _get_report_values(self, docids, data=None):
        return _vals(self.env, "hr.in.report.wizard.exp.product_analytic", docids)
