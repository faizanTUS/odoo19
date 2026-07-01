# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

import base64
import csv
import io

from odoo import models

from .payroll_report_domain import payslip_confirmed_states


def _payslip_line_total(line):
    if "total" in line._fields:
        return line.total
    return line.amount


def _employee_bank_account_for_payroll(employee):
    """Odoo 19 hr.employee: primary_bank_account_id / bank_account_ids (legacy bank_account_id)."""
    if not employee:
        return False
    emp = employee.sudo()
    if "primary_bank_account_id" in emp._fields and emp.primary_bank_account_id:
        return emp.primary_bank_account_id
    if "bank_account_id" in emp._fields and getattr(emp, "bank_account_id", False):
        return emp.bank_account_id
    if "bank_account_ids" in emp._fields and emp.bank_account_ids:
        return emp.bank_account_ids[0]
    return False


class HrInReportWizardPayRegister(models.TransientModel):
    _name = "hr.in.report.wizard.pay.register"
    _description = "Payroll register"
    _inherit = ["hr.in.report.wizard.mixin"]

    def _professional_pdf_sum_column_keys(self):
        return ["net", "gross"]

    def _pdf_report_xmlid(self):
        return "india_hr_reports.action_report_pay_register"

    def _payslip_domain(self):
        dom = [
            ("company_id", "in", self.company_ids.ids),
            ("state", "in", payslip_confirmed_states(self.env)),
            ("date_from", "<=", self.date_to),
            ("date_to", ">=", self.date_from),
        ]
        dom += self._report_employee_domain()
        if self.department_ids:
            dom.append(("employee_id.department_id", "in", self.department_ids.ids))
        return dom

    def _get_dataset(self):
        self.ensure_one()
        slips = self.env["hr.payslip"].search(self._payslip_domain(), order="employee_id")
        self._enforce_row_cap(len(slips))
        cols = [
            ("employee", "Employee"),
            ("number", "Payslip"),
            ("batch", "Batch / struct"),
            ("date_from", "From"),
            ("date_to", "To"),
            ("net", "Net"),
            ("gross", "Gross"),
        ]
        rows = []
        for s in slips:
            net = sum(
                _payslip_line_total(l) for l in s.line_ids.filtered(lambda l: l.code == "NET")
            )
            gross_lines = s.line_ids.filtered(
                lambda l: l.category_id and l.category_id.code == "GROSS"
            )
            gross = sum(_payslip_line_total(l) for l in gross_lines) or sum(
                _payslip_line_total(l) for l in s.line_ids
            )
            rows.append(
                {
                    "employee": s.employee_id.display_name,
                    "number": getattr(s, "number", False) or getattr(s, "name", False) or "",
                    "batch": s.payslip_run_id.name if s.payslip_run_id else (s.struct_id.name if s.struct_id else ""),
                    "date_from": s.date_from,
                    "date_to": s.date_to,
                    "net": net,
                    "gross": gross,
                }
            )
        return {
            "title": "Payroll register",
            "filename": "in_pay_register",
            "sheet_name": "payroll",
            "columns": cols,
            "rows": rows,
        }


class HrInReportWizardPayBank(models.TransientModel):
    _name = "hr.in.report.wizard.pay.bank"
    _description = "Bank net pay advice"
    _inherit = ["hr.in.report.wizard.mixin"]

    def _professional_pdf_sum_column_keys(self):
        return ["net"]

    def _pdf_report_xmlid(self):
        return "india_hr_reports.action_report_pay_bank"

    def _payslip_domain(self):
        dom = [
            ("company_id", "in", self.company_ids.ids),
            ("state", "in", payslip_confirmed_states(self.env)),
            ("date_from", "<=", self.date_to),
            ("date_to", ">=", self.date_from),
        ]
        dom += self._report_employee_domain()
        if self.department_ids:
            dom.append(("employee_id.department_id", "in", self.department_ids.ids))
        return dom

    def _get_dataset(self):
        self.ensure_one()
        slips = self.env["hr.payslip"].search(self._payslip_domain(), order="employee_id")
        self._enforce_row_cap(len(slips))
        cols = [
            ("employee", "Employee"),
            ("bank", "Bank account"),
            ("ifsc", "IFSC / BIC"),
            ("net", "Net pay"),
            ("currency", "Currency"),
        ]
        rows = []
        for s in slips:
            net = sum(
                _payslip_line_total(l) for l in s.line_ids.filtered(lambda l: l.code == "NET")
            )
            bank_acc = _employee_bank_account_for_payroll(s.employee_id)
            bic = ""
            if bank_acc:
                bic = getattr(bank_acc, "bank_bic", None) or (
                    bank_acc.bank_id.bic if bank_acc.bank_id else ""
                )
            rows.append(
                {
                    "employee": s.employee_id.display_name,
                    "bank": bank_acc.acc_number if bank_acc else "",
                    "ifsc": bic,
                    "net": net,
                    "currency": s.currency_id.name,
                }
            )
        return {
            "title": "Bank net pay advice",
            "filename": "in_pay_bank_advice",
            "sheet_name": "bank",
            "columns": cols,
            "rows": rows,
        }

    def action_export_csv(self):
        self.ensure_one()
        ds = self._get_dataset()
        self._enforce_row_cap(len(ds["rows"]))
        buf = io.StringIO()
        keys = [c[0] for c in ds["columns"]]
        writer = csv.writer(buf)
        writer.writerow([c[1] for c in ds["columns"]])
        for row in ds["rows"]:
            writer.writerow([row.get(k, "") for k in keys])
        content = buf.getvalue().encode("utf-8")
        fname = (ds.get("filename") or "bank") + ".csv"
        att = self.env["ir.attachment"].create(
            {
                "name": fname,
                "type": "binary",
                "datas": base64.b64encode(content),
                "mimetype": "text/csv",
            }
        )
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % att.id,
            "target": "self",
        }
