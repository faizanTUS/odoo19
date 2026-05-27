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


class ReportInPf(models.AbstractModel):
    _name = "report.IndiaHrReports.pay_in_pf_document"
    _description = "PDF PF register"

    @api.model
    def _get_report_values(self, docids, data=None):
        return _vals(self.env, "hr.in.report.wizard.in.pf", docids)


class ReportInEsi(models.AbstractModel):
    _name = "report.IndiaHrReports.pay_in_esi_document"
    _description = "PDF ESI register"

    @api.model
    def _get_report_values(self, docids, data=None):
        return _vals(self.env, "hr.in.report.wizard.in.esi", docids)


class ReportInPt(models.AbstractModel):
    _name = "report.IndiaHrReports.pay_in_pt_document"
    _description = "PDF PT register"

    @api.model
    def _get_report_values(self, docids, data=None):
        return _vals(self.env, "hr.in.report.wizard.in.pt", docids)


class ReportInLwf(models.AbstractModel):
    _name = "report.IndiaHrReports.pay_in_lwf_document"
    _description = "PDF LWF register"

    @api.model
    def _get_report_values(self, docids, data=None):
        return _vals(self.env, "hr.in.report.wizard.in.lwf", docids)


class ReportInTds(models.AbstractModel):
    _name = "report.IndiaHrReports.pay_in_tds_document"
    _description = "PDF TDS summary"

    @api.model
    def _get_report_values(self, docids, data=None):
        return _vals(self.env, "hr.in.report.wizard.in.tds", docids)
