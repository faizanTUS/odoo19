# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, models


def _report_vals(env, wizard_model, docids):
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


class ReportHubHeadcountPdf(models.AbstractModel):
    _name = "report.IndiaHrReports.hub_pdf_headcount_document"
    _description = "PDF headcount wizard (professional layout)"

    @api.model
    def _get_report_values(self, docids, data=None):
        return _report_vals(self.env, "hr.in.report.wizard.hub.headcount", docids)


class ReportHubSnapshotPdf(models.AbstractModel):
    _name = "report.IndiaHrReports.hub_pdf_snapshot_document"
    _description = "PDF employee snapshot wizard (professional layout)"

    @api.model
    def _get_report_values(self, docids, data=None):
        return _report_vals(self.env, "hr.in.report.wizard.hub.snapshot", docids)
