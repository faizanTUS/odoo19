# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, models


class ReportFleetAssign(models.AbstractModel):
    _name = "report.IndiaHrReportscommunity.report_fleet_assign_document"
    _description = "PDF fleet assignment"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["hr.in.report.wizard.fleet.assign"].browse(docids)
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
