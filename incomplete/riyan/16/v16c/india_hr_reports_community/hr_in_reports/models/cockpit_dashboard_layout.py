# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
"""Reference-style HR dashboard layout payload (cards, KPIs, sidebar, footer)."""

from datetime import date, datetime, timedelta

import pytz

from odoo import _, fields
from odoo.tools import format_amount, format_date

from .cockpit_data import (
    _context_today,
    cockpit_attendance_company_domain,
    cockpit_attendance_date_range_domain,
    cockpit_attendance_today_domain,
    cockpit_company_ids,
    cockpit_date_range,
    cockpit_hr_filters_attendance_domain,
    cockpit_hr_filters_employee_domain,
    cockpit_hr_filters_expense_domain,
    cockpit_hr_filters_leave_domain,
    cockpit_hr_filters_payslip_domain,
    cockpit_int_ids,
    cockpit_leave_overlap_domain,
    cockpit_module_installed,
    cockpit_payslip_overlap_domain,
    cockpit_employee_scope_domain,
    payslip_confirmed_states_for_cockpit,
)


def _fmt_int(n):
    try:
        return f"{int(n):,}"
    except (TypeError, ValueError):
        return "0"


def _greeting_prefix(env):
    tzname = env.user.tz or "UTC"
    try:
        tz = pytz.timezone(tzname)
        hour = datetime.now(tz).hour
    except Exception:
        hour = datetime.now().hour
    if hour < 12:
        return _("Good morning")
    if hour < 17:
        return _("Good afternoon")
    return _("Good evening")


def _m2o_id_from_read(val):
    if not val:
        return False
    if isinstance(val, (list, tuple)):
        return int(val[0]) if val[0] else False
    if isinstance(val, int):
        return val
    return False


def _domain_as_lists(domain):
    """RPC/JSON-safe domain: tuples → lists, dates → strings."""
    out = []
    for term in domain:
        if isinstance(term, (list, tuple)) and len(term) == 3:
            row = list(term)
            for i, v in enumerate(row):
                if isinstance(v, datetime):
                    row[i] = fields.Datetime.to_string(v)
                elif isinstance(v, date):
                    row[i] = fields.Date.to_string(v)
            out.append(row)
        else:
            out.append(term)
    return out


def cockpit_employee_country_rows(env, Emp, emp_dom, limit=15, search_limit=12000):
    """Count active employees by country using the first available field per employee.

    Priority: private country (address) → country of birth. The company country
    is intentionally not used as a fallback: employees with no nationality set
    must show under "Unknown" (matches Odoo's own "None" grouping), not under
    the first/active company.
    """
    priority = []
    for fname in ("private_country_id", "country_of_birth"):
        if fname in Emp._fields:
            priority.append(fname)
    if not priority:
        return [], []
    domain = list(emp_dom) + [("active", "=", True)]
    data = Emp.search_read(domain, priority, limit=search_limit)
    counts = {}
    unknown = 0
    for rec in data:
        cid = False
        for fname in priority:
            cid = _m2o_id_from_read(rec.get(fname))
            if cid:
                break
        if not cid:
            unknown += 1
            continue
        counts[cid] = counts.get(cid, 0) + 1
    if not counts and not unknown:
        return [], priority
    Country = env["res.country"].sudo()
    rows = []
    for cid, cnt in sorted(counts.items(), key=lambda x: -x[1])[:limit]:
        c = Country.browse(cid)
        rows.append(
            {
                "label": c.name or _("Unknown"),
                "count": int(cnt),
                "code": c.code or "",
            }
        )
    if unknown:
        rows.append(
            {
                "label": _("Unknown"),
                "count": int(unknown),
                "code": "",
            }
        )
    return rows, priority


def cockpit_satisfaction_payload(env, date_from, date_to, companies, emp_dom):
    """Dynamic satisfaction gauge.

    Returns a dict ``{value, max, count, hint, source}`` (or ``None`` when no
    data is available). The score is on a 1–5 scale.

    Priority order:
      1) ``survey.user_input``: completed responses with ``scoring_percentage``
         inside the period. Restricted to partners that map to employees in
         the current scope when applicable. The average percentage / 20 gives
         a 1–5 value.
      2) ``hr.appraisal``: weighted average position of ``assessment_note``
         for done appraisals in the period. Notes ordered by ``sequence desc``
         get the highest position, matching the existing perf bars convention.
    """
    # 1) Surveys
    if cockpit_module_installed(env, "survey") and "survey.user_input" in env:
        Inp = env["survey.user_input"].sudo()
        dt_from = fields.Datetime.to_datetime(date_from)
        dt_to = fields.Datetime.to_datetime(date_to) + timedelta(
            hours=23, minutes=59, seconds=59
        )
        dom = [
            ("state", "=", "done"),
            ("scoring_percentage", ">", 0),
            ("end_datetime", ">=", dt_from),
            ("end_datetime", "<=", dt_to),
        ]
        Emp = env["hr.employee"].sudo()
        scope_emps = Emp.search(emp_dom + [("active", "=", True)])
        partner_ids = set()
        for fname in ("work_contact_id", "user_partner_id"):
            if fname in Emp._fields:
                for pid in scope_emps.mapped(f"{fname}.id"):
                    if pid:
                        partner_ids.add(pid)
        if "user_id" in Emp._fields:
            for emp in scope_emps:
                user = emp.user_id
                if user and user.partner_id:
                    partner_ids.add(user.partner_id.id)
        if partner_ids:
            dom.append(("partner_id", "in", list(partner_ids)))
        rows = Inp.read_group(dom, ["scoring_percentage:avg"], [], lazy=False)
        if rows:
            avg_pct = rows[0].get("scoring_percentage") or 0
            count = int(rows[0].get("__count") or 0)
            if count and avg_pct:
                value = max(0.0, min(5.0, round(float(avg_pct) / 20.0, 1)))
                return {
                    "value": value,
                    "max": 5.0,
                    "count": count,
                    "hint": _("Based on %s survey response(s)") % count,
                    "source": "survey",
                }

    # 2) Appraisals (used as a proxy when no surveys exist)
    if cockpit_module_installed(env, "hr_appraisal") and env.registry.get(
        "hr.appraisal"
    ):
        Appraisal = env["hr.appraisal"].sudo()
        notes = (
            env["hr.appraisal.note"]
            .sudo()
            .search(
                [("company_id", "in", list(companies) + [False])],
                order="sequence desc",
            )
        )
        n = len(notes)
        if n >= 2:
            position = {note.id: n - i for i, note in enumerate(notes)}
            app_dom = [
                ("state", "=", "3_done"),
                ("date_close", ">=", date_from),
                ("date_close", "<=", date_to),
                ("company_id", "in", list(companies)),
                ("assessment_note", "!=", False),
            ]
            scope_emps = env["hr.employee"].sudo().search(emp_dom)
            if scope_emps:
                app_dom.append(("employee_id", "in", scope_emps.ids))
            rows = Appraisal.read_group(app_dom, [], ["assessment_note"], lazy=False)
            total_w, total_c = 0.0, 0
            for row in rows:
                note_val = row.get("assessment_note")
                nid = (
                    note_val[0]
                    if isinstance(note_val, (list, tuple))
                    else note_val
                )
                cnt = int(row.get("__count") or 0)
                pos = position.get(nid)
                if pos and cnt:
                    total_w += pos * cnt
                    total_c += cnt
            if total_c:
                avg_pos = total_w / total_c
                value = (
                    round(1 + (avg_pos - 1) * 4.0 / (n - 1), 1)
                    if n > 1
                    else round(avg_pos, 1)
                )
                value = max(0.0, min(5.0, value))
                return {
                    "value": value,
                    "max": 5.0,
                    "count": total_c,
                    "hint": _(
                        "Average rating across %s completed appraisal(s)"
                    )
                    % total_c,
                    "source": "appraisal",
                }

    return None


def cockpit_employee_window_action(name, domain, group_by):
    """Client action dict: list first, then graph and pivot."""
    ctx = {}
    if group_by:
        ctx["group_by"] = group_by
    return {
        "type": "ir.actions.act_window",
        "name": name,
        "res_model": "hr.employee",
        "view_mode": "tree,graph,pivot",
        "views": [
            [False, "tree"],
            [False, "graph"],
            [False, "pivot"],
        ],
        "domain": _domain_as_lists(domain),
        "target": "current",
        "context": ctx,
    }


def _views_from_view_mode(view_mode):
    """Build ``views`` tuples for the web client (required by action_service._preprocessAction)."""
    raw = (view_mode or "tree,form").strip()
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if not parts:
        parts = ["tree", "form"]
    return [[False, p] for p in parts]


def cockpit_act_window(name, model, domain, view_mode="tree,form", group_by=None, context_extra=None):
    """JSON-safe act_window dict for arbitrary models (merged cockpit domains)."""
    ctx = dict(context_extra or {})
    if group_by:
        ctx["group_by"] = group_by
    return {
        "type": "ir.actions.act_window",
        "name": name,
        "res_model": model,
        "view_mode": view_mode,
        "views": _views_from_view_mode(view_mode),
        "domain": _domain_as_lists(domain),
        "target": "current",
        "context": ctx,
    }


def cockpit_xmlid_action(env, xmlid):
    """Return xmlid string for doAction if the record exists."""
    return xmlid if env.ref(xmlid, raise_if_not_found=False) else None


def collect_dashboard_layout(env, filters):
    """Build JSON layout matching the HR Cockpit reference design."""
    date_from, date_to = cockpit_date_range(env, filters, default_days=30)
    companies = cockpit_company_ids(env, filters)
    today = _context_today(env)
    Emp = env["hr.employee"]
    emp_dom = cockpit_employee_scope_domain(filters, companies, env=env)
    total_employees = Emp.search_count(emp_dom + [("active", "=", True)])
    region_rows, country_priority = cockpit_employee_country_rows(env, Emp, emp_dom, limit=12)

    joiners_dom = (
        emp_dom
        + [
            ("active", "=", True),
            ("create_date", ">=", fields.Datetime.to_datetime(date_from)),
            (
                "create_date",
                "<=",
                fields.Datetime.to_datetime(date_to) + timedelta(hours=23, minutes=59, seconds=59),
            ),
        ]
    )
    joiners = Emp.search_count(joiners_dom)

    on_leave_today = 0
    present_today = 0
    leave_today_dom = []
    att_today_dom = []
    if cockpit_module_installed(env, "hr_holidays"):
        Leave = env["hr.leave"]
        leave_today_dom = (
            cockpit_leave_overlap_domain(today, today, companies)
            + cockpit_hr_filters_leave_domain(filters, env=env)
            + [
                ("state", "=", "validate"),
            ]
        )
        on_leave_today = Leave.search_count(leave_today_dom)

    if cockpit_module_installed(env, "hr_attendance"):
        Att = env["hr.attendance"]
        att_today_dom = (
            cockpit_attendance_today_domain(env, today)
            + cockpit_attendance_company_domain(companies)
            + cockpit_hr_filters_attendance_domain(filters, env=env)
        )
        emps_today = Att.read_group(att_today_dom, [], ["employee_id"], lazy=False)
        present_today = len([r for r in emps_today if r.get("employee_id")])

    payroll_cost = 0.0
    currency = env.company.currency_id
    payroll_donut = {"labels": [], "datasets": [{"label": _("Payroll"), "data": []}]}
    if cockpit_module_installed(env, "hr_payroll") and "hr.payslip" in env:
        Slip = env["hr.payslip"]
        states = payslip_confirmed_states_for_cockpit(env)
        slip_dom = (
            cockpit_payslip_overlap_domain(date_from, date_to, companies)
            + cockpit_hr_filters_payslip_domain(filters, env=env)
            + [("state", "in", states)]
        )
        slips = Slip.search(slip_dom)
        payroll_cost = sum(slips.mapped("net_wage")) if slips and "net_wage" in Slip._fields else 0.0
        if slips and env.registry.get("hr.payslip.line"):
            Line = env["hr.payslip.line"]
            rows = Line.read_group(
                [("slip_id", "in", slips.ids), ("category_id", "!=", False)],
                ["total:sum"],
                ["category_id"],
                lazy=False,
            )
            labels = []
            data = []
            for row in sorted(rows, key=lambda r: -(r.get("total") or 0))[:6]:
                cat = row.get("category_id")
                if cat:
                    labels.append(cat[1] if isinstance(cat, (list, tuple)) else _("Category"))
                else:
                    labels.append(_("Other"))
                data.append(float(row.get("total") or 0))
            if labels:
                payroll_donut = {
                    "labels": labels,
                    "datasets": [{"label": _("Amount"), "data": data}],
                }

    workforce_chart = {"labels": [], "datasets": [{"label": _("Headcount"), "data": []}]}
    if "contract_type_id" in Emp._fields:
        rows = Emp.read_group(
            emp_dom + [("active", "=", True), ("contract_type_id", "!=", False)],
            [],
            ["contract_type_id"],
            lazy=False,
        )
        labels = []
        data = []
        for row in sorted(rows, key=lambda r: -(r.get("__count", 0) or 0)):
            ct = row.get("contract_type_id")
            labels.append(ct[1] if isinstance(ct, (list, tuple)) else _("Type"))
            data.append(int(row.get("__count", 0) or 0))
        if not labels:
            labels = [_("Not specified")]
            data = [total_employees or 0]
        workforce_chart = {
            "labels": labels,
            "datasets": [{"label": _("Employees"), "data": data}],
        }
    else:
        workforce_chart = {
            "labels": [_("Employees")],
            "datasets": [{"label": _("Headcount"), "data": [total_employees or 0]}],
        }
    leave_period_dom = []
    leave_metrics = [
        {"label": _("Time off"), "value": "—"},
        {"label": _("—"), "value": "—"},
        {"label": _("—"), "value": "—"},
        {"label": _("—"), "value": "—"},
    ]
    leave_by_state_chart = {"labels": [], "datasets": [{"label": _("Requests"), "data": []}]}
    leave_footer_action = None
    if cockpit_module_installed(env, "hr_holidays"):
        Leave = env["hr.leave"]
        leave_period_dom = cockpit_leave_overlap_domain(date_from, date_to, companies) + cockpit_hr_filters_leave_domain(
            filters, env=env
        )
        dom = leave_period_dom
        leave_metrics = [
            {"label": _("Outstanding requests"), "value": _fmt_int(Leave.search_count(dom))},
            {"label": _("To approve"), "value": _fmt_int(Leave.search_count(dom + [("state", "=", "confirm")]))},
            {"label": _("Approved"), "value": _fmt_int(Leave.search_count(dom + [("state", "=", "validate")]))},
            {"label": _("Refused"), "value": _fmt_int(Leave.search_count(dom + [("state", "=", "refuse")]))},
        ]
        rows = Leave.read_group(dom, [], ["state"], lazy=False)
        state_labels = dict(Leave._fields["state"]._description_selection(env))
        lbls = []
        dvals = []
        for row in sorted(rows, key=lambda r: -(r.get("__count", 0) or 0)):
            code = row.get("state") or ""
            lbls.append(state_labels.get(code, code or _("Unknown")))
            dvals.append(int(row.get("__count", 0) or 0))
        if lbls:
            leave_by_state_chart = {
                "labels": lbls,
                "datasets": [{"label": _("Time off"), "data": dvals}],
            }
        leave_footer_action = cockpit_act_window(
            _("Time off"),
            "hr.leave",
            dom,
            "kanban,list,form,calendar,activity",
            group_by=["state"],
        )

    funnel_stages = []
    if cockpit_module_installed(env, "hr_recruitment"):
        App = env["hr.applicant"]
        app_dom = [("active", "=", True), ("company_id", "in", companies)]
        if cockpit_int_ids(filters, "department_ids"):
            app_dom.append(("department_id", "in", cockpit_int_ids(filters, "department_ids")))
        rows = App.read_group(app_dom, [], ["stage_id"], lazy=False)
        max_c = max((int(r.get("__count", 0) or 0) for r in rows), default=1)
        for row in sorted(rows, key=lambda r: -(r.get("__count", 0) or 0))[:8]:
            st = row.get("stage_id")
            if isinstance(st, (list, tuple)) and st:
                name = st[1] or _("None")
            else:
                name = _("None")
            cnt = int(row.get("__count", 0) or 0)
            funnel_stages.append(
                {
                    "label": name,
                    "count": cnt,
                    "width_pct": max(8, int(100 * cnt / max_c)),
                }
            )

    claims_list = []
    exp_dom = []
    claims_footer_action = None
    if cockpit_module_installed(env, "hr_expense"):
        Exp = env["hr.expense"]
        exp_dom = (
            [
                ("date", ">=", date_from),
                ("date", "<=", date_to),
                ("company_id", "in", companies),
            ]
            + cockpit_hr_filters_expense_domain(filters, env=env)
        )
        claims_footer_action = cockpit_act_window(
            _("Expenses"),
            "hr.expense",
            exp_dom,
            "list,kanban,pivot,graph",
        )
        rows = Exp.read_group(exp_dom, ['total_amount:sum'], ["state"], lazy=False)
        state_labels = dict(Exp._fields["state"]._description_selection(env))
        for row in sorted(rows, key=lambda r: -(r.get("total_amount", 0) or 0)):
            code = row.get("state") or ""
            claims_list.append(
                {
                    "label": state_labels.get(code, code or _("Unknown")),
                    "value": format_amount(env, row.get("total_amount") or 0, currency),
                }
            )

    att_half = {"labels": [], "datasets": [{"label": _("Sessions"), "data": []}], "half_donut": True}
    att_footer_action = None
    if cockpit_module_installed(env, "hr_attendance"):
        Att = env["hr.attendance"]
        att_base_dom = (
            cockpit_attendance_date_range_domain(env, date_from, date_to)
            + cockpit_attendance_company_domain(companies)
            + cockpit_hr_filters_attendance_domain(filters, env=env)
        )
        full = Att.search_count(att_base_dom + [("check_out", "!=", False), ("worked_hours", ">=", 7)])
        std = Att.search_count(
            att_base_dom + [("check_out", "!=", False), ("worked_hours", ">=", 3), ("worked_hours", "<", 7)]
        )
        short = Att.search_count(att_base_dom + [("check_out", "!=", False), ("worked_hours", "<", 3)])
        opn = Att.search_count(att_base_dom + [("check_out", "=", False)])
        att_half = {
            "labels": [_("Long shift"), _("Standard"), _("Short"), _("Open check-out")],
            "datasets": [{"label": _("Attendance"), "data": [full, std, short, opn]}],
            "half_donut": True,
        }
        att_footer_action = cockpit_act_window(
            _("Attendance"),
            "hr.attendance",
            att_base_dom,
            "list,graph,pivot,form",
            group_by=["employee_id"],
        )

    perf_bars = {
        "labels": [_("5★"), _("4★"), _("3★"), _("2★"), _("1★")],
        "datasets": [{"label": _("Reviews (sample)"), "data": [0, 0, 0, 0, 0]}],
        "horizontal": True,
        "placeholder": True,
    }
    appraisal_footer_action = None
    if cockpit_module_installed(env, "hr_appraisal") and env.registry.get("hr.appraisal"):
        Appraisal = env["hr.appraisal"]
        app_dom = [
            ("state", "=", "3_done"),
            ("date_close", ">=", date_from),
            ("date_close", "<=", date_to),
            ("company_id", "in", companies),
        ]
        app_dom += cockpit_hr_filters_leave_domain(filters, env=env)
        rows = Appraisal.read_group(app_dom, [], ["assessment_note"], lazy=False)
        notes = env["hr.appraisal.note"].sudo().search(
            [("company_id", "in", companies + [False])], order="sequence desc"
        )
        labels = []
        data = []
        counts_by_id = {}
        unrated = 0
        for row in rows:
            note = row.get("assessment_note")
            cnt = int(row.get("__count", 0) or 0)
            if note:
                counts_by_id[note[0] if isinstance(note, (list, tuple)) else note] = cnt
            else:
                unrated += cnt
        for n in notes:
            labels.append(n.name)
            data.append(counts_by_id.get(n.id, 0))
        if unrated:
            labels.append(_("Unrated"))
            data.append(unrated)
        if any(data):
            perf_bars = {
                "labels": labels,
                "datasets": [{"label": _("Done appraisals"), "data": data}],
                "horizontal": True,
            }
        appraisal_footer_action = cockpit_act_window(
            _("Appraisals"),
            "hr.appraisal",
            app_dom,
            "list,kanban,pivot,graph,form",
            group_by=["assessment_note"],
        )

    birthdays = []
    employees = Emp.search(emp_dom + [("active", "=", True), ("birthday", "!=", False)], limit=80)
    for emp in employees:
        if not emp.birthday:
            continue
        b = emp.birthday.replace(year=today.year)
        if b < today:
            b = b.replace(year=today.year + 1)
        if today <= b <= today + timedelta(days=60):
            birthdays.append(
                {
                    "name": emp.name,
                    "day": format_date(env, b, date_format="medium"),
                }
            )
    birthdays = sorted(birthdays, key=lambda x: x["day"])[:8]

    period_label = "%s – %s" % (
        format_date(env, fields.Date.to_date(date_from)),
        format_date(env, fields.Date.to_date(date_to)),
    )

    cost_label = format_amount(env, payroll_cost, currency) if payroll_cost else "—"

    footer_presence = list(region_rows)[:10]
    emp_active_dom = list(emp_dom) + [("active", "=", True)]
    group_for_country = (
        country_priority[:1]
        if country_priority
        else (["company_country_id"] if "company_country_id" in Emp._fields else [])
    )
    workforce_footer_action = cockpit_employee_window_action(
        _("Workforce distribution"),
        emp_active_dom,
        ["contract_type_id"] if "contract_type_id" in Emp._fields else [],
    )
    by_country_footer_action = cockpit_employee_window_action(
        _("Employees by country"),
        emp_active_dom,
        group_for_country,
    )
    by_region_empty_hint = _(
        "No per-employee country yet. Set Private Country, Country of Birth, or set the company country."
    )

    payroll_footer_action = None
    if cockpit_module_installed(env, "hr_payroll") and "hr.payslip" in env:
        payroll_list_dom = (
            cockpit_payslip_overlap_domain(date_from, date_to, companies)
            + cockpit_hr_filters_payslip_domain(filters, env=env)
        )
        payroll_footer_action = cockpit_act_window(
            _("Payslips"),
            "hr.payslip",
            payroll_list_dom,
            "list,kanban,form,activity",
            group_by=["state"],
        )

    recruitment_footer_action = cockpit_xmlid_action(env, "hr_recruitment.crm_case_categ0_act_job")
    perf_footer_action = appraisal_footer_action or cockpit_employee_window_action(
        _("Employees"), emp_active_dom, []
    )
    satisfaction_data = cockpit_satisfaction_payload(
        env, date_from, date_to, companies, emp_dom
    )
    if satisfaction_data and satisfaction_data.get("source") == "survey":
        satisfaction_footer_action = cockpit_xmlid_action(
            env, "survey.action_survey_user_input"
        ) or cockpit_xmlid_action(env, "survey.action_survey_form")
    elif satisfaction_data and satisfaction_data.get("source") == "appraisal":
        satisfaction_footer_action = appraisal_footer_action
    else:
        satisfaction_footer_action = (
            cockpit_xmlid_action(env, "survey.action_survey_user_input")
            or cockpit_xmlid_action(env, "survey.action_survey_form")
            or appraisal_footer_action
        )

    kpi_present_action = None
    if cockpit_module_installed(env, "hr_attendance") and att_today_dom:
        kpi_present_action = cockpit_act_window(
            _("Present today"),
            "hr.attendance",
            att_today_dom,
            "list,graph,pivot",
            group_by=["employee_id"],
        )
    kpi_leave_action = None
    if cockpit_module_installed(env, "hr_holidays") and leave_today_dom:
        kpi_leave_action = cockpit_act_window(
            _("On leave today"),
            "hr.leave",
            leave_today_dom,
            "kanban,list,form,calendar,activity",
            group_by=["employee_id"],
        )
    kpi_payroll_action = payroll_footer_action
    kpi_headcount_action = cockpit_employee_window_action(_("Total employees"), emp_active_dom, [])
    kpi_joiners_action = cockpit_act_window(
        _("New joiners"),
        "hr.employee",
        joiners_dom,
        "list,kanban,form,activity",
    )

    kpis = [
        {
            "key": "present",
            "label": _("Present today"),
            "value": _fmt_int(present_today),
            "accent": "success",
            **({"action": kpi_present_action} if kpi_present_action else {}),
        },
        {
            "key": "leave_now",
            "label": _("On leave today"),
            "value": _fmt_int(on_leave_today),
            "accent": "warning",
            **({"action": kpi_leave_action} if kpi_leave_action else {}),
        },
        {
            "key": "pay_cost",
            "label": _("Payroll cost"),
            "value": cost_label,
            "accent": "pay",
            **({"action": kpi_payroll_action} if kpi_payroll_action else {}),
        },
        {
            "key": "headcount",
            "label": _("Total employees"),
            "value": _fmt_int(total_employees),
            "accent": "primary",
            **({"action": kpi_headcount_action} if kpi_headcount_action else {}),
        },
        {
            "key": "joiners",
            "label": _("New joiners"),
            "value": _fmt_int(joiners),
            "accent": "info",
            **({"action": kpi_joiners_action} if kpi_joiners_action else {}),
        },
    ]

    col1 = []
    if cockpit_module_installed(env, "hr_attendance"):
        col1.append(
            {
                "id": "attendance_overview",
                "title": _("Attendance overview"),
                "card_type": "chart",
                "chart": {"id": "att_half", "type": "doughnut", "title": "", **att_half},
                "footer": _("Attendance analysis"),
                "footer_action": att_footer_action,
            }
        )
    if cockpit_module_installed(env, "hr_holidays"):
        col1.append(
            {
                "id": "leave_overview",
                "title": _("Leave overview"),
                "card_type": "metric_grid",
                "metrics": leave_metrics,
                "footer": _("View all"),
                "footer_action": leave_footer_action,
            }
        )
        col1.append(
            {
                "id": "leave_distribution",
                "title": _("Time off by status"),
                "card_type": "chart",
                "chart": {"id": "leave_states", "type": "doughnut", "title": "", **leave_by_state_chart},
                "footer": _("View requests"),
                "footer_action": leave_footer_action,
            }
        )
    payroll_card = None
    if cockpit_module_installed(env, "hr_payroll") and "hr.payslip" in env:
        payroll_card = {
            "id": "payroll_summary",
            "title": _("Payroll summary"),
            "card_type": "chart",
            "chart": {"id": "payroll_sum", "type": "doughnut", "title": "", **payroll_donut},
        }
        if payroll_footer_action:
            payroll_card["footer"] = _("View payroll")
            payroll_card["footer_action"] = payroll_footer_action

    col2 = [
        {
            "id": "workforce",
            "title": _("Workforce distribution"),
            "card_type": "chart",
            "chart": {"id": "workforce", "type": "doughnut", "title": "", **workforce_chart},
            "footer": _("View full report"),
            "footer_action": workforce_footer_action,
        },
        {
            "id": "by_region",
            "title": _("Employees by country"),
            "card_type": "map_list",
            "rows": region_rows,
            "footer": _("View full report"),
            "footer_action": by_country_footer_action,
            "empty_hint": by_region_empty_hint,
        },
        {
            "id": "recruitment",
            "title": _("Recruitment pipeline"),
            "card_type": "funnel",
            "funnel": funnel_stages,
            **(
                {"footer": _("Open recruitment"), "footer_action": recruitment_footer_action}
                if recruitment_footer_action
                else {}
            ),
        },
        {
            "id": "claims",
            "title": _("Claims summary"),
            "card_type": "simple_list",
            "list": claims_list,
            **(
                {"footer": _("View expenses"), "footer_action": claims_footer_action}
                if claims_footer_action
                else {}
            ),
        },
    ]

    col3 = [
        {
            "id": "performance",
            "title": _("Performance overview"),
            "card_type": "chart",
            "chart": {"id": "perf", "type": "bar", "title": "", **perf_bars},
            "footer": _("Appraisals"),
            "footer_action": perf_footer_action,
        },
        {
            "id": "satisfaction",
            "title": _("Employee satisfaction"),
            "card_type": "gauge",
            "gauge": (
                {
                    "value": satisfaction_data["value"],
                    "max": satisfaction_data["max"],
                    "hint": satisfaction_data["hint"],
                }
                if satisfaction_data
                else {
                    "value": None,
                    "max": 5.0,
                    "display": "—",
                    "hint": _(
                        "No survey responses or completed appraisals "
                        "in this period."
                    ),
                }
            ),
            "footer": _("Details"),
            "footer_action": satisfaction_footer_action,
        },
    ]
    if payroll_card:
        col3.append(payroll_card)

    def _quick(env, icon, label, xmlid):
        act = env.ref(xmlid, raise_if_not_found=False)
        if not act or act._name not in ("ir.actions.act_window", "ir.actions.client"):
            return None
        return {"icon": icon, "label": label, "action_id": act.id, "action_type": act._name}

    quick_links = [
        x
        for x in (
            _quick(env, "fa-calendar", _("Time off"), "hr_holidays.hr_leave_action_my_request"),
            _quick(env, "fa-user", _("My profile"), "hr.open_view_employee_list_my"),
            _quick(env, "fa-graduation-cap", _("Courses"), "website_slides.slide_channel_action_overview"),
            _quick(env, "fa-money", _("My payslip"), "hr_payroll.action_view_hr_payslip_month_form"),
            _quick(env, "fa-sitemap", _("Org chart"), "hr_org_chart.action_hr_employee_org_chart"),
            _quick(env, "fa-comments", _("Discuss"), "mail.action_discuss"),
        )
        if x
    ]

    return {
        "greeting": {"prefix": _greeting_prefix(env), "name": env.user.name},
        "period_label": period_label,
        "kpis": kpis,
        "columns": [col1, col2, col3],
        "sidebar": {
            "birthdays": birthdays,
            "quick_links": quick_links,
        },
        "footer_presence": footer_presence,
    }
