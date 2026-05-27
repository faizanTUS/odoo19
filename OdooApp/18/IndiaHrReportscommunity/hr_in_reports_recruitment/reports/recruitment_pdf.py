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


class ReportRecFunnel(models.AbstractModel):
    _name = "report.IndiaHrReportscommunity.pay_rec_funnel_document"
    _description = "PDF hiring funnel"

    @api.model
    def _get_report_values(self, docids, data=None):
        return _vals(self.env, "hr.in.report.wizard.rec.funnel", docids)


class ReportRecTth(models.AbstractModel):
    _name = "report.IndiaHrReportscommunity.pay_rec_tth_document"
    _description = "PDF time to hire"

    @api.model
    def _get_report_values(self, docids, data=None):
        return _vals(self.env, "hr.in.report.wizard.rec.tth", docids)


class ReportRecSource(models.AbstractModel):
    _name = "report.IndiaHrReportscommunity.pay_rec_source_document"
    _description = "PDF source mix"

    @api.model
    def _get_report_values(self, docids, data=None):
        return _vals(self.env, "hr.in.report.wizard.rec.source", docids)
