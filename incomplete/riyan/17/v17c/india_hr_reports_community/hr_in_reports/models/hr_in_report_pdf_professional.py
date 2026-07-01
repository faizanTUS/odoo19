# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
"""Professional PDF context for hub + attendance wizards (same layout pattern as leave reports)."""

from datetime import date, datetime

from odoo import _, fields


def _to_float(val):
    if val is None or val is False:
        return 0.0
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def _format_cell(env, val):
    if val is None:
        return ""
    if hasattr(val, "_name") and hasattr(val, "ids"):
        return val.display_name or ""
    if isinstance(val, datetime):
        from odoo.tools import format_datetime

        return format_datetime(env, val, dt_format="short") or ""
    if isinstance(val, date):
        from odoo.tools import format_date

        return format_date(env, val) or ""
    if isinstance(val, float):
        from odoo.tools import formatLang

        return formatLang(env, val, digits=2)
    return val


def professional_filter_rows(record):
    env = record.env
    from odoo.tools import format_date

    rows = [
        {
            "label": _("Period"),
            "value": _("%(df)s to %(dt)s")
            % {
                "df": format_date(env, record.date_from),
                "dt": format_date(env, record.date_to),
            },
        },
        {
            "label": _("Companies"),
            "value": ", ".join(record.company_ids.mapped("name")) or "-",
        },
    ]
    if record.department_ids:
        rows.append(
            {
                "label": _("Departments"),
                "value": ", ".join(record.department_ids.mapped("name")),
            }
        )
    else:
        rows.append({"label": _("Departments"), "value": _("All departments")})
    if record.employee_ids:
        rows.append(
            {
                "label": _("Employees"),
                "value": _("%(count)s selected") % {"count": len(record.employee_ids)},
            }
        )
    else:
        rows.append({"label": _("Employees"), "value": _("All employees in scope")})
    return rows


def professional_subtitle(record):
    env = record.env
    if record._name == "hr.in.report.wizard.hub.headcount":
        return _(
            "Opening and closing headcount on contract dates, with optional movement lines "
            "for hires, contract ends, and departures."
        )
    if record._name == "hr.in.report.wizard.hub.snapshot":
        return _(
            "Employee master data as of the report end date: identification, job, contacts, "
            "and reporting lines."
        )
    if record._name == "hr.in.report.wizard.att.daily":
        return _("Check-in and check-out lines with worked hours for each attendance in the period.")
    if record._name == "hr.in.report.wizard.att.monthly":
        return _("Worked hours per employee for each calendar day in the selected window (max 62 days).")
    if record._name == "hr.in.report.wizard.att.exceptions":
        return _("Attendance lines still open (missing check-out) in the period.")
    if record._name == "hr.in.report.wizard.att.ot":
        return _(
            "Overtime hours per employee: sum of daily worked hours above the regular-hours threshold."
        )
    if record._name == "hr.in.report.wizard.pay.register":
        return _(
            "Validated or paid payslips in the selected window: reference, pay period, net and gross totals."
        )
    if record._name == "hr.in.report.wizard.pay.bank":
        return _(
            "Net pay per employee with bank account details for the selected window (CSV also available on the wizard)."
        )
    if record._name == "hr.in.report.wizard.in.pf":
        return _(
            "Payslip lines for validated or paid payslips in the period whose rule codes match PF / EPF-style contributions."
        )
    if record._name == "hr.in.report.wizard.in.esi":
        return _(
            "Payslip lines for validated or paid payslips in the period whose rule codes match ESI / ESIC-style contributions."
        )
    if record._name == "hr.in.report.wizard.in.pt":
        return _(
            "Professional tax lines from confirmed payslips (PT, PTD, PROFTAX-style codes; generic 'PT' substring matches are avoided)."
        )
    if record._name == "hr.in.report.wizard.in.lwf":
        return _(
            "Labour welfare fund lines from confirmed payslips whose codes match LWF-style rules."
        )
    if record._name == "hr.in.report.wizard.in.tds":
        return _(
            "Income tax / TDS deduction lines from confirmed payslips (TDS, ITAX, and related code patterns)."
        )
    if record._name == "hr.in.report.wizard.plan.coverage":
        return _(
            "Planning shifts overlapping the period: resource, role, allocated hours, and draft or published status."
        )
    if record._name == "hr.in.report.wizard.plan.under_over":
        return _(
            "Planned hours per resource versus assumed weekly capacity times the number of weeks in the date range."
        )
    if record._name == "hr.in.report.wizard.rec.funnel":
        return _(
            "Applicants created in the period, grouped by current recruitment stage (one row per stage with counts)."
        )
    if record._name == "hr.in.report.wizard.rec.tth":
        return _(
            "Applications with a close date in the period: days from first application timestamp to hire/close date."
        )
    if record._name == "hr.in.report.wizard.rec.source":
        return _(
            "Applicants created in the period grouped by UTM source; empty source is shown as direct or none."
        )
    if record._name == "hr.in.report.wizard.exp.consolidated":
        return _("Employee-level totals of approved and submitted expenses in the selected period.")
    if record._name == "hr.in.report.wizard.exp.product_analytic":
        return _("Expense lines with product and analytic distribution for the selected period.")
    if record._name == "hr.in.report.wizard.fleet.assign":
        return _("Fleet vehicles with driver, company, acquisition date, and odometer reading.")
    return ""


def professional_column_align_classes(column_keys, record):
    if record._name == "hr.in.report.wizard.att.monthly":
        return ["text-end" if k != "employee" else "text-start" for k in column_keys]
    if record._name == "hr.in.report.wizard.pay.register":
        right = {"net", "gross", "date_from", "date_to"}
        return ["text-end" if k in right else "text-start" for k in column_keys]
    if record._name == "hr.in.report.wizard.pay.bank":
        right = {"net"}
        return ["text-end" if k in right else "text-start" for k in column_keys]
    if record._name.startswith("hr.in.report.wizard.in."):
        right = {"amount"}
        return ["text-end" if k in right else "text-start" for k in column_keys]
    if record._name == "hr.in.report.wizard.plan.coverage":
        right = {"hours", "start", "end"}
        return ["text-end" if k in right else "text-start" for k in column_keys]
    if record._name == "hr.in.report.wizard.plan.under_over":
        right = {"planned_hours", "capacity", "delta"}
        return ["text-end" if k in right else "text-start" for k in column_keys]
    if record._name in (
        "hr.in.report.wizard.rec.funnel",
        "hr.in.report.wizard.rec.source",
    ):
        right = {"count"}
        return ["text-end" if k in right else "text-start" for k in column_keys]
    if record._name == "hr.in.report.wizard.rec.tth":
        right = {"days", "create_date", "date_closed"}
        return ["text-end" if k in right else "text-start" for k in column_keys]
    if record._name == "hr.in.report.wizard.exp.consolidated":
        right = {"total_amount"}
        return ["text-end" if k in right else "text-start" for k in column_keys]
    if record._name == "hr.in.report.wizard.exp.product_analytic":
        right = {"amount"}
        return ["text-end" if k in right else "text-start" for k in column_keys]
    if record._name == "hr.in.report.wizard.fleet.assign":
        right = {"odometer"}
        return ["text-end" if k in right else "text-start" for k in column_keys]
    right = {"value", "worked_hours", "ot_hours"}
    return ["text-end" if k in right else "text-start" for k in column_keys]


def professional_column_meta(column_labels, column_keys, record):
    classes = professional_column_align_classes(column_keys, record)
    return [{"label": lab, "class": cls} for lab, cls in zip(column_labels, classes)]


def professional_table_rows(row_values, column_meta):
    rows = []
    for row in row_values:
        cells = []
        for i, val in enumerate(row):
            cls = column_meta[i]["class"] if i < len(column_meta) else "text-start"
            cells.append({"value": val, "class": cls})
        rows.append(cells)
    return rows


def professional_summary_metrics(record, lines, column_keys, column_labels):
    env = record.env
    from odoo.tools import format_datetime, formatLang

    metrics = [{"label": _("Detail lines"), "value": str(len(lines))}]
    sum_keys = record._professional_pdf_sum_column_keys()
    for key in sum_keys:
        if key not in column_keys:
            continue
        idx = column_keys.index(key)
        label = column_labels[idx] if idx < len(column_labels) else key
        total = sum(_to_float(line.get(key)) for line in lines)
        metrics.append(
            {
                "label": _("Total %(field)s") % {"field": label},
                "value": formatLang(env, total, digits=2),
            }
        )
    return metrics


def enrich_professional_pdf_context(record, ctx):
    """Extend base mixin PDF context with table-based professional layout keys."""
    env = record.env
    lines = ctx.get("lines") or []
    column_keys = ctx.get("column_keys") or []
    column_labels = ctx.get("column_labels") or []
    company = record.company_ids[:1] or env.company
    filter_rows = professional_filter_rows(record)
    summary_metrics = professional_summary_metrics(record, lines, column_keys, column_labels)
    from odoo.tools import format_datetime

    row_values = [[_format_cell(env, line.get(k, "")) for k in column_keys] for line in lines]
    column_meta = professional_column_meta(column_labels, column_keys, record)
    table_rows = professional_table_rows(row_values, column_meta)
    prepared_on = format_datetime(env, fields.Datetime.now(), dt_format="medium")
    subtitle = professional_subtitle(record)
    ctx.update(
        {
            "company": company,
            "o": record,
            "layout_document_title": ctx.get("doc_title") or "",
            "report_wide_matrix": record._name in ("hr.in.report.wizard.att.monthly", "hr.in.report.wizard.hub.snapshot"),
            "report_subtitle": subtitle,
            "filter_rows": filter_rows,
            "summary_metrics": summary_metrics,
            "column_meta": column_meta,
            "table_rows": table_rows,
            "row_values": row_values,
            "section_filters_label": _("Applied filters"),
            "section_detail_label": _("Detail"),
            "section_summary_label": _("Summary"),
            "prepared_footer": _("Prepared on %(when)s - Prepared by %(who)s")
            % {"when": prepared_on, "who": env.user.display_name},
            "table_empty_message": _("No records match the selected filters."),
        }
    )
    return ctx
