# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import fields, models


def _applicant_display_name(applicant):
    return (applicant.partner_name or applicant.name or "").strip()


class HrInReportWizardRecFunnel(models.TransientModel):
    _name = "hr.in.report.wizard.rec.funnel"
    _description = "Hiring funnel"
    _inherit = ["hr.in.report.wizard.rec.mixin", "hr.in.report.wizard.mixin"]

    def _filter_summary_text(self):
        parts = [super()._filter_summary_text()]
        if self.job_ids:
            parts.append("Jobs: %s" % ", ".join(self.job_ids.mapped("name")))
        return " | ".join(parts)

    def _professional_pdf_sum_column_keys(self):
        return ["count"]

    def _pdf_report_xmlid(self):
        return "IndiaHrReportscommunity.action_report_rec_funnel"

    def _get_dataset(self):
        self.ensure_one()
        apps = self.env["hr.applicant"].search(self._applicant_domain_created_in_period())
        self._enforce_row_cap(len(apps))
        none_label = self.env._("(No stage)")
        counts = {}
        for a in apps:
            key = a.stage_id.name if a.stage_id else none_label
            counts[key] = counts.get(key, 0) + 1
        cols = [("stage", "Stage"), ("count", "Applicants")]
        rows = [{"stage": k, "count": v} for k, v in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]
        return {
            "title": "Hiring funnel",
            "filename": "in_rec_funnel",
            "sheet_name": "funnel",
            "columns": cols,
            "rows": rows,
        }


class HrInReportWizardRecTth(models.TransientModel):
    _name = "hr.in.report.wizard.rec.tth"
    _description = "Time to hire"
    _inherit = ["hr.in.report.wizard.rec.mixin", "hr.in.report.wizard.mixin"]

    def _filter_summary_text(self):
        parts = [super()._filter_summary_text()]
        if self.job_ids:
            parts.append("Jobs: %s" % ", ".join(self.job_ids.mapped("name")))
        return " | ".join(parts)

    def _professional_pdf_sum_column_keys(self):
        return ["days"]

    def _pdf_report_xmlid(self):
        return "IndiaHrReportscommunity.action_report_rec_tth"

    def _get_dataset(self):
        self.ensure_one()
        dom = self._applicant_domain_closed_in_period() + [("active", "in", [True, False])]
        apps = self.env["hr.applicant"].search(dom, order="date_closed,id")
        self._enforce_row_cap(len(apps))
        cols = [
            ("name", "Applicant"),
            ("job", "Job"),
            ("create_date", "Applied"),
            ("date_closed", "Closed"),
            ("days", "Days (closed − created)"),
        ]
        rows = []
        for a in apps:
            days_val = ""
            if a.day_close is not False and a.day_close is not None:
                days_val = round(float(a.day_close), 2)
            elif a.create_date and a.date_closed:
                delta = fields.Datetime.to_datetime(a.date_closed) - fields.Datetime.to_datetime(
                    a.create_date
                )
                days_val = round(delta.total_seconds() / 86400.0, 2)
            rows.append(
                {
                    "name": _applicant_display_name(a),
                    "job": a.job_id.name or "",
                    "create_date": a.create_date,
                    "date_closed": a.date_closed,
                    "days": days_val,
                }
            )
        return {
            "title": "Time to hire",
            "filename": "in_rec_time_to_hire",
            "sheet_name": "tth",
            "columns": cols,
            "rows": rows,
        }


class HrInReportWizardRecSource(models.TransientModel):
    _name = "hr.in.report.wizard.rec.source"
    _description = "Source effectiveness"
    _inherit = ["hr.in.report.wizard.rec.mixin", "hr.in.report.wizard.mixin"]

    def _filter_summary_text(self):
        parts = [super()._filter_summary_text()]
        if self.job_ids:
            parts.append("Jobs: %s" % ", ".join(self.job_ids.mapped("name")))
        return " | ".join(parts)

    def _professional_pdf_sum_column_keys(self):
        return ["count"]

    def _pdf_report_xmlid(self):
        return "IndiaHrReportscommunity.action_report_rec_source"

    def _get_dataset(self):
        self.ensure_one()
        apps = self.env["hr.applicant"].search(self._applicant_domain_created_in_period())
        self._enforce_row_cap(len(apps))
        direct = self.env._("Direct / none")
        counts = {}
        for a in apps:
            src = a.source_id.name if a.source_id else direct
            counts[src] = counts.get(src, 0) + 1
        cols = [("source", "Source"), ("count", "Applicants")]
        rows = [{"source": k, "count": v} for k, v in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]
        return {
            "title": "Source effectiveness",
            "filename": "in_rec_source_mix",
            "sheet_name": "sources",
            "columns": cols,
            "rows": rows,
        }
