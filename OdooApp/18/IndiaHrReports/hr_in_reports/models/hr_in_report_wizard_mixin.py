# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError

from .hr_in_report_export_utils import build_xlsx_bytes, xlsx_attachment


class HrInReportWizardMixin(models.AbstractModel):
    """Shared filters + XLSX/PDF export for HR India report wizards."""

    _name = "hr.in.report.wizard.mixin"
    _description = "HR India report wizard mixin"

    _report_requires_hrms_manager = False

    date_from = fields.Date(
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(day=1),
    )
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    company_ids = fields.Many2many(
        "res.company",
        string="Companies",
        required=True,
        default=lambda self: self._default_company_ids(),
    )
    department_ids = fields.Many2many("hr.department", string="Departments")
    employee_ids = fields.Many2many("hr.employee", string="Employees")

    def _default_company_ids(self):
        return self.env.companies

    @api.model
    def _max_export_rows(self):
        param = self.env["ir.config_parameter"].sudo().get_param(
            "IndiaHrReports.max_export_rows", "50000"
        )
        try:
            return max(100, int(param))
        except ValueError:
            return 50000

    def _company_domain(self):
        return [("company_id", "in", self.company_ids.ids)]

    def _validate_report_access(self):
        """Enforce HR Reports groups and optional HRMS-only reports."""
        access = self.env["hr.in.report.access"]
        access.assert_reports_access()
        if self._report_requires_hrms_manager:
            access.assert_hrms_manager()

    def _report_employee_domain(self, field_name="employee_id"):
        """Domain fragment: HRMS = optional filter; employees = self + subordinates."""
        return self.env["hr.in.report.access"].report_employee_domain(
            self.employee_ids.ids,
            field_name=field_name,
        )

    def _report_hr_employee_domain(self):
        """Same as _report_employee_domain for searches on hr.employee (id field)."""
        return self._report_employee_domain(field_name="id")

    def _report_employee_ids(self):
        """Resolved employee ids for reports that need an explicit id list."""
        return self.env["hr.in.report.access"].resolve_employee_ids(self.employee_ids.ids)

    def _filter_summary_text(self):
        parts = [
            "%s - %s" % (self.date_from, self.date_to),
            "Companies: %s" % (", ".join(self.company_ids.mapped("name")) or "-"),
        ]
        if self.department_ids:
            parts.append("Departments: %s" % ", ".join(self.department_ids.mapped("name")))
        if self.employee_ids:
            parts.append("Employees: %d selected" % len(self.employee_ids))
        return " | ".join(parts)

    def _get_dataset(self):
        """Return dict: title (str), columns [(key, label)], rows [dict]."""
        raise NotImplementedError

    def _enforce_row_cap(self, count):
        cap = self._max_export_rows()
        if count > cap:
            raise UserError(
                self.env._(
                    "This export would return %(count)s rows, above the limit of %(cap)s. "
                    "Narrow filters, split by department, or raise hr_in_reports.max_export_rows."
                )
                % {"count": count, "cap": cap}
            )

    def _rows_for_xlsx(self, ds):
        cols = ds["columns"]
        keys = [c[0] for c in cols]
        return [[row.get(k, "") for k in keys] for row in ds["rows"]]

    def _professional_pdf_layout(self):
        """Use standard QWeb shell + table layout (hub, attendance, payroll wizards)."""
        return self._name.startswith(
            (
                "hr.in.report.wizard.hub.",
                "hr.in.report.wizard.att.",
                "hr.in.report.wizard.pay.",
                "hr.in.report.wizard.in.",
                "hr.in.report.wizard.plan.",
                "hr.in.report.wizard.rec.",
                "hr.in.report.wizard.exp.",
                "hr.in.report.wizard.fleet.",
            )
        )

    def _professional_pdf_sum_column_keys(self):
        """Column keys from the detail dataset to total in the PDF summary (optional)."""
        return []

    def action_export_xlsx(self):
        self.ensure_one()
        self._validate_report_access()
        ds = self._get_dataset()
        self._enforce_row_cap(len(ds["rows"]))
        headers = [c[1] for c in ds["columns"]]
        keys = [c[0] for c in ds["columns"]]
        rows = self._rows_for_xlsx(ds)
        from odoo import fields
        from odoo.tools import format_datetime

        from .hr_in_report_pdf_professional import (
            professional_filter_rows,
            professional_subtitle,
            professional_summary_metrics,
        )

        company = self.company_ids[:1] or self.env.company
        header = {
            "title": ds.get("title") or self.env._("Report"),
            "company": company.display_name,
            "subtitle": professional_subtitle(self),
            "filter_rows": professional_filter_rows(self),
            "summary_rows": professional_summary_metrics(self, ds["rows"], keys, headers),
            "footer": self.env._("Prepared on %(when)s - Prepared by %(who)s")
            % {
                "when": format_datetime(self.env, fields.Datetime.now(), dt_format="medium"),
                "who": self.env.user.display_name,
            },
            "section_filters_label": self.env._("Applied filters"),
            "section_detail_label": self.env._("Detail"),
            "section_summary_label": self.env._("Summary"),
        }
        content = build_xlsx_bytes(
            ds.get("sheet_name", "report")[:31],
            headers,
            rows,
            env=self.env,
            xlsx_options=ds.get("xlsx_options"),
            header=header,
        )
        fname = (ds.get("filename") or "report") + ".xlsx"
        att = xlsx_attachment(self.env, fname, content)
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % att.id,
            "target": "self",
        }

    def _get_pdf_render_context(self):
        self.ensure_one()
        self._validate_report_access()
        ds = self._get_dataset()
        self._enforce_row_cap(len(ds["rows"]))
        keys = [c[0] for c in ds["columns"]]
        row_values = [[line.get(k, "") for k in keys] for line in ds["rows"]]
        ctx = {
            "doc_title": ds["title"],
            "column_keys": keys,
            "column_labels": [c[1] for c in ds["columns"]],
            "lines": ds["rows"],
            "row_values": row_values,
            "filter_summary": self._filter_summary_text(),
        }
        if self._professional_pdf_layout():
            from .hr_in_report_pdf_professional import enrich_professional_pdf_context

            ctx = enrich_professional_pdf_context(self, ctx)
        return ctx

    def action_export_pdf(self):
        self.ensure_one()
        self._validate_report_access()
        xmlid = self._pdf_report_xmlid()
        if not xmlid:
            raise UserError(self.env._("PDF report is not configured for this wizard."))
        report = self.env.ref(xmlid, raise_if_not_found=False)
        if not report:
            raise UserError(self.env._("Missing PDF report definition."))
        return report.report_action(self)

    def _pdf_report_xmlid(self):
        """Each concrete wizard returns e.g. hr_in_reports.action_report_hub_headcount."""
        return False
