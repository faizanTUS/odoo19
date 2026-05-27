# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
"""Payslip line filters for Indian statutory registers (codes follow l10n_in_hr_payroll structures)."""

from odoo.addons.IndiaHrReports.hr_in_reports_payroll.models.payroll_report_domain import payslip_confirmed_states

# Substrings / tokens for hr.payslip.line.code (uppercased). Adjust via custom rules if needed.
PF_CODE_TOKENS = (
    "PF",
    "EPF",
    "PFEMP",
    "PFEMPL",
    "PFWAGE",
    "EPS",
    "PFE",
    "ERPF",
    "EPMF",
    "ENPFC",
    "VPF",
)
ESI_CODE_TOKENS = ("ESI", "ESIC", "ESIEMP", "ESIEMPR", "ESICS", "ESICF")
LWF_CODE_TOKENS = ("LWF", "LWFE", "LWFEMP", "LWFEMPR")
TDS_CODE_TOKENS = (
    "TDS",
    "ITAX",
    "INCTAX",
    "INCOME",
    "SURCHARGE",
    "CESS",
    "EDU_CESS",
    "EDUCESS",
    "SECTION_80",
    "SEC80",
    "RELIEF",
    "CHALLAN",
)


def statutory_payslip_line_domain(wizard):
    """Same confirmed payslip window as hub payroll reports (section 9), on slip lines."""
    dom = [
        ("slip_id.company_id", "in", wizard.company_ids.ids),
        ("slip_id.state", "in", payslip_confirmed_states(wizard.env)),
        ("slip_id.date_from", "<=", wizard.date_to),
        ("slip_id.date_to", ">=", wizard.date_from),
    ]
    dom += wizard.env["hr.in.report.access"].report_employee_domain(
        wizard.employee_ids.ids,
        field_name="slip_id.employee_id",
    )
    if wizard.department_ids:
        dom.append(("slip_id.employee_id.department_id", "in", wizard.department_ids.ids))
    return dom


def line_matches_pf(code):
    if not code:
        return False
    c = code.strip().upper()
    return any(tok in c for tok in PF_CODE_TOKENS)


def line_matches_esi(code):
    if not code:
        return False
    c = code.strip().upper()
    return any(tok in c for tok in ESI_CODE_TOKENS)


def line_matches_lwf(code):
    if not code:
        return False
    c = code.strip().upper()
    return any(tok in c for tok in LWF_CODE_TOKENS)


def line_matches_professional_tax(code):
    """Avoid CPT-style false positives ('PT' inside unrelated codes)."""
    if not code:
        return False
    c = code.strip().upper()
    if c in ("PT", "PTD"):
        return True
    return any(
        tok in c
        for tok in (
            "PROFTAX",
            "PTAX",
            "PROF_TAX",
            "PROFT",
            "PROF.TAX",
            "PTAXD",
            "PT_DED",
        )
    )


def line_matches_tds(code):
    if not code:
        return False
    c = code.strip().upper()
    # Exact codes only for very short tokens; avoid 'IT' substring inside e.g. INT (interest).
    if c in ("IT", "TDS"):
        return True
    return any(tok in c for tok in TDS_CODE_TOKENS)
