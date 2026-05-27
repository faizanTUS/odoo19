# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
"""Shared date / company scope for HR cockpit providers (JSON payloads)."""

from datetime import date, datetime, timedelta

from odoo import fields


def _context_today(env):
    """fields.Date.context_today expects a recordset (uses record.env.tz), not a bare Environment."""
    return fields.Date.context_today(env["res.users"].browse(env.uid))


def cockpit_company_ids(env, filters):
    fc = filters or {}
    raw = fc.get("company_ids")
    if raw:
        return [int(x) for x in raw]
    return list(env.context.get("allowed_company_ids") or [env.company.id])


def cockpit_parse_date(val, default):
    if val is None or val is False:
        return default
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, str):
        return fields.Date.to_date(val[:10])
    return fields.Date.to_date(val)


def cockpit_date_range(env, filters, default_days=30):
    """Inclusive [date_from, date_to]; default last default_days+1 calendar days."""
    fc = filters or {}
    today = _context_today(env)
    date_to = cockpit_parse_date(fc.get("date_to"), today)
    date_from = cockpit_parse_date(fc.get("date_from"), today - timedelta(days=default_days))
    if date_from > date_to:
        date_from = date_to - timedelta(days=default_days)
    return date_from, date_to


def cockpit_attendance_company_domain(company_ids):
    return ["|", ("employee_id.company_id", "=", False), ("employee_id.company_id", "in", company_ids)]


def cockpit_leave_company_domain(company_ids):
    return ["|", ("company_id", "=", False), ("company_id", "in", company_ids)]


def cockpit_leave_overlap_domain(date_from, date_to, company_ids):
    """Leaves whose request window overlaps [date_from, date_to]."""
    return (
        cockpit_leave_company_domain(company_ids)
        + [
            ("request_date_from", "<=", date_to),
            ("request_date_to", ">=", date_from),
        ]
    )


def cockpit_payslip_overlap_domain(date_from, date_to, company_ids):
    return [
        ("company_id", "in", company_ids),
        ("date_from", "<=", date_to),
        ("date_to", ">=", date_from),
    ]


def _cockpit_int_ids(filters, key):
    raw = (filters or {}).get(key) or []
    out = []
    for x in raw:
        try:
            out.append(int(x))
        except (TypeError, ValueError):
            continue
    return out


def _cockpit_hierarchy_domain(env, field_name="employee_id"):
    if not env:
        return []
    return env["hr.in.report.access"].cockpit_employee_domain(field_name=field_name)


def cockpit_hr_filters_attendance_domain(filters, env=None):
    """hr.attendance: scope by employee / their department / job."""
    fc = filters or {}
    dom = list(_cockpit_hierarchy_domain(env))
    eids = _cockpit_int_ids(fc, "employee_ids")
    if eids:
        dom.append(("employee_id", "in", eids))
    dids = _cockpit_int_ids(fc, "department_ids")
    if dids:
        dom.append(("employee_id.department_id", "in", dids))
    jids = _cockpit_int_ids(fc, "job_ids")
    if jids:
        dom.append(("employee_id.job_id", "in", jids))
    return dom


def cockpit_hr_filters_leave_domain(filters, env=None):
    """hr.leave: stored department_id + employee job for job filter."""
    fc = filters or {}
    dom = list(_cockpit_hierarchy_domain(env))
    eids = _cockpit_int_ids(fc, "employee_ids")
    if eids:
        dom.append(("employee_id", "in", eids))
    dids = _cockpit_int_ids(fc, "department_ids")
    if dids:
        dom.append(("department_id", "in", dids))
    jids = _cockpit_int_ids(fc, "job_ids")
    if jids:
        dom.append(("employee_id.job_id", "in", jids))
    return dom


def cockpit_hr_filters_payslip_domain(filters, env=None):
    """hr.payslip: employee, department, job on slip / employee."""
    fc = filters or {}
    dom = list(_cockpit_hierarchy_domain(env))
    eids = _cockpit_int_ids(fc, "employee_ids")
    if eids:
        dom.append(("employee_id", "in", eids))
    dids = _cockpit_int_ids(fc, "department_ids")
    if dids:
        dom.append(("employee_id.department_id", "in", dids))
    jids = _cockpit_int_ids(fc, "job_ids")
    if jids:
        dom.append(("job_id", "in", jids))
    return dom


def cockpit_module_installed(env, module_name):
    mod = env["ir.module.module"].sudo().search([("name", "=", module_name)], limit=1)
    return bool(mod and mod.state == "installed")


def cockpit_employee_company_domain(company_ids):
    if not company_ids:
        return [("id", "=", False)]
    return ["|", ("company_id", "=", False), ("company_id", "in", company_ids)]


def cockpit_hr_filters_employee_domain(filters, env=None):
    """Domain fragment on hr.employee for cockpit HR scope."""
    fc = filters or {}
    dom = list(_cockpit_hierarchy_domain(env, field_name="id"))
    eids = _cockpit_int_ids(fc, "employee_ids")
    if eids:
        dom.append(("id", "in", eids))
    dids = _cockpit_int_ids(fc, "department_ids")
    if dids:
        dom.append(("department_id", "in", dids))
    jids = _cockpit_int_ids(fc, "job_ids")
    if jids:
        dom.append(("job_id", "in", jids))
    return dom


def cockpit_employee_scope_domain(filters, company_ids, env=None):
    """Full domain for hr.employee (company + optional HR filters)."""
    return cockpit_employee_company_domain(company_ids) + cockpit_hr_filters_employee_domain(
        filters, env=env
    )


def cockpit_hr_filters_expense_domain(filters, env=None):
    """hr.expense: employee / department / job."""
    fc = filters or {}
    dom = list(_cockpit_hierarchy_domain(env))


    eids = _cockpit_int_ids(fc, "employee_ids")
    if eids:
        dom.append(("employee_id", "in", eids))
    dids = _cockpit_int_ids(fc, "department_ids")
    if dids:
        dom.append(("department_id", "in", dids))
    jids = _cockpit_int_ids(fc, "job_ids")
    if jids:
        dom.append(("employee_id.job_id", "in", jids))
    return dom


def payslip_confirmed_states_for_cockpit(env):
    """Confirmed payslip states without depending on hr_in_reports_payroll."""
    if env.registry.get("hr.payslip") is None:
        return ["validated", "paid"]
    field = env["hr.payslip"]._fields.get("state")
    if not field:
        return ["validated", "paid"]
    sel = field.selection
    if callable(sel):
        try:
            sel = sel(env["hr.payslip"])
        except TypeError:
            sel = sel()
    if not sel:
        return ["validated", "paid"]
    codes = {row[0] for row in sel}
    preferred = [s for s in ("validated", "paid", "done") if s in codes]
    if preferred:
        return preferred
    return [c for c in sorted(codes) if c not in ("draft", "cancel")]


def cockpit_int_ids(filters, key):
    """Public helper: parse int id lists from cockpit filter dict."""
    return _cockpit_int_ids(filters, key)
