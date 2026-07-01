# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

import base64
import csv
import io

from odoo import models

from .indian_statutory_filters import (
    line_matches_esi,
    line_matches_lwf,
    line_matches_pf,
    line_matches_professional_tax,
    line_matches_tds,
    statutory_payslip_line_domain,
)


def _line_total(line):
    return line.total if "total" in line._fields else line.amount


class HrInReportWizardInPf(models.TransientModel):
    _name = "hr.in.report.wizard.in.pf"
    _description = "PF contribution register"
    _inherit = ["hr.in.report.wizard.mixin"]

    def _professional_pdf_sum_column_keys(self):
        return ["amount"]

    def _pdf_report_xmlid(self):
        return "india_hr_reports.action_report_in_pf"

    def _pf_lines(self):
        lines = self.env["hr.payslip.line"].search(statutory_payslip_line_domain(self))
        return lines.filtered(lambda l: line_matches_pf(l.code))

    def _get_dataset(self):
        self.ensure_one()
        lines = self._pf_lines()
        self._enforce_row_cap(len(lines))
        cols = [
            ("employee", "Employee"),
            ("slip", "Payslip"),
            ("code", "Rule code"),
            ("name", "Name"),
            ("amount", "Amount"),
        ]
        rows = []
        for l in sorted(lines, key=lambda x: (x.slip_id.employee_id.name or "", x.code or "")):
            rows.append(
                {
                    "employee": l.slip_id.employee_id.display_name,
                    "slip": getattr(l.slip_id, "number", False)
                    or getattr(l.slip_id, "name", False)
                    or "",
                    "code": l.code,
                    "name": l.name,
                    "amount": _line_total(l),
                }
            )
        return {
            "title": "PF contribution register",
            "filename": "in_in_pf_register",
            "sheet_name": "pf",
            "columns": cols,
            "rows": rows,
        }

    def action_export_csv(self):
        self.ensure_one()
        ds = self._get_dataset()
        self._enforce_row_cap(len(ds["rows"]))
        buf = io.StringIO()
        keys = [c[0] for c in ds["columns"]]
        w = csv.writer(buf)
        w.writerow([c[1] for c in ds["columns"]])
        for row in ds["rows"]:
            w.writerow([row.get(k, "") for k in keys])
        raw = buf.getvalue().encode("utf-8")
        att = self.env["ir.attachment"].create(
            {
                "name": ds["filename"] + ".csv",
                "type": "binary",
                "datas": base64.b64encode(raw),
                "mimetype": "text/csv",
            }
        )
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % att.id,
            "target": "self",
        }


class HrInReportWizardInEsi(models.TransientModel):
    _name = "hr.in.report.wizard.in.esi"
    _description = "ESI register"
    _inherit = ["hr.in.report.wizard.mixin"]

    def _professional_pdf_sum_column_keys(self):
        return ["amount"]

    def _pdf_report_xmlid(self):
        return "india_hr_reports.action_report_in_esi"

    def _esi_lines(self):
        lines = self.env["hr.payslip.line"].search(statutory_payslip_line_domain(self))
        return lines.filtered(lambda l: line_matches_esi(l.code))

    def _get_dataset(self):
        self.ensure_one()
        lines = self._esi_lines()
        self._enforce_row_cap(len(lines))
        cols = [
            ("employee", "Employee"),
            ("slip", "Payslip"),
            ("code", "Rule code"),
            ("name", "Name"),
            ("amount", "Amount"),
        ]
        rows = []
        for l in sorted(lines, key=lambda x: (x.slip_id.employee_id.name or "", x.code or "")):
            rows.append(
                {
                    "employee": l.slip_id.employee_id.display_name,
                    "slip": getattr(l.slip_id, "number", False)
                    or getattr(l.slip_id, "name", False)
                    or "",
                    "code": l.code,
                    "name": l.name,
                    "amount": _line_total(l),
                }
            )
        return {
            "title": "ESI register",
            "filename": "in_in_esi_register",
            "sheet_name": "esi",
            "columns": cols,
            "rows": rows,
        }

    def action_export_csv(self):
        self.ensure_one()
        ds = self._get_dataset()
        self._enforce_row_cap(len(ds["rows"]))
        buf = io.StringIO()
        keys = [c[0] for c in ds["columns"]]
        w = csv.writer(buf)
        w.writerow([c[1] for c in ds["columns"]])
        for row in ds["rows"]:
            w.writerow([row.get(k, "") for k in keys])
        raw = buf.getvalue().encode("utf-8")
        att = self.env["ir.attachment"].create(
            {
                "name": ds["filename"] + ".csv",
                "type": "binary",
                "datas": base64.b64encode(raw),
                "mimetype": "text/csv",
            }
        )
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % att.id,
            "target": "self",
        }


class HrInReportWizardInPt(models.TransientModel):
    _name = "hr.in.report.wizard.in.pt"
    _description = "Professional tax register"
    _inherit = ["hr.in.report.wizard.mixin"]

    def _professional_pdf_sum_column_keys(self):
        return ["amount"]

    def _pdf_report_xmlid(self):
        return "india_hr_reports.action_report_in_pt"

    def _get_dataset(self):
        self.ensure_one()
        lines = self.env["hr.payslip.line"].search(statutory_payslip_line_domain(self))
        lines = lines.filtered(lambda l: line_matches_professional_tax(l.code))
        self._enforce_row_cap(len(lines))
        cols = [
            ("employee", "Employee"),
            ("slip", "Payslip"),
            ("code", "Code"),
            ("name", "Name"),
            ("amount", "Amount"),
        ]
        rows = [
            {
                "employee": l.slip_id.employee_id.display_name,
                "slip": getattr(l.slip_id, "number", False)
                or getattr(l.slip_id, "name", False)
                or "",
                "code": l.code,
                "name": l.name,
                "amount": _line_total(l),
            }
            for l in sorted(lines, key=lambda x: (x.slip_id.employee_id.name or "", x.code or ""))
        ]
        return {
            "title": "Professional tax register",
            "filename": "in_in_pt_register",
            "sheet_name": "pt",
            "columns": cols,
            "rows": rows,
        }


class HrInReportWizardInLwf(models.TransientModel):
    _name = "hr.in.report.wizard.in.lwf"
    _description = "LWF register"
    _inherit = ["hr.in.report.wizard.mixin"]

    def _professional_pdf_sum_column_keys(self):
        return ["amount"]

    def _pdf_report_xmlid(self):
        return "india_hr_reports.action_report_in_lwf"

    def _get_dataset(self):
        self.ensure_one()
        lines = self.env["hr.payslip.line"].search(statutory_payslip_line_domain(self))
        lines = lines.filtered(lambda l: line_matches_lwf(l.code))
        self._enforce_row_cap(len(lines))
        cols = [
            ("employee", "Employee"),
            ("slip", "Payslip"),
            ("code", "Code"),
            ("name", "Name"),
            ("amount", "Amount"),
        ]
        rows = [
            {
                "employee": l.slip_id.employee_id.display_name,
                "slip": getattr(l.slip_id, "number", False)
                or getattr(l.slip_id, "name", False)
                or "",
                "code": l.code,
                "name": l.name,
                "amount": _line_total(l),
            }
            for l in sorted(lines, key=lambda x: (x.slip_id.employee_id.name or "", x.code or ""))
        ]
        return {
            "title": "LWF register",
            "filename": "in_in_lwf_register",
            "sheet_name": "lwf",
            "columns": cols,
            "rows": rows,
        }


class HrInReportWizardInTds(models.TransientModel):
    _name = "hr.in.report.wizard.in.tds"
    _description = "TDS summary"
    _inherit = ["hr.in.report.wizard.mixin"]

    def _professional_pdf_sum_column_keys(self):
        return ["amount"]

    def _pdf_report_xmlid(self):
        return "india_hr_reports.action_report_in_tds"

    def _get_dataset(self):
        self.ensure_one()
        lines = self.env["hr.payslip.line"].search(statutory_payslip_line_domain(self))
        lines = lines.filtered(lambda l: line_matches_tds(l.code))
        self._enforce_row_cap(len(lines))
        cols = [
            ("employee", "Employee"),
            ("slip", "Payslip"),
            ("code", "Code"),
            ("name", "Name"),
            ("amount", "Amount"),
        ]
        rows = [
            {
                "employee": l.slip_id.employee_id.display_name,
                "slip": getattr(l.slip_id, "number", False)
                or getattr(l.slip_id, "name", False)
                or "",
                "code": l.code,
                "name": l.name,
                "amount": _line_total(l),
            }
            for l in sorted(lines, key=lambda x: (x.slip_id.employee_id.name or "", x.code or ""))
        ]
        return {
            "title": "TDS summary",
            "filename": "in_in_tds_summary",
            "sheet_name": "tds",
            "columns": cols,
            "rows": rows,
        }
