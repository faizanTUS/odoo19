# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
"""Shared professional layout metadata for leave PDF/XLSX exports."""

from datetime import date, datetime

from odoo import _, fields
from odoo.tools import format_date, format_datetime, formatLang


def _to_float(val):
    if val is None or val is False:
        return 0.0
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def _format_cell(env, val):
    if hasattr(val, "_name") and hasattr(val, "ids"):
        return val.display_name or ""
    if isinstance(val, datetime):
        return format_datetime(env, val, dt_format="short") or ""
    if isinstance(val, date):
        return format_date(env, val) or ""
    if isinstance(val, float):
        return formatLang(env, val, digits=2)
    return val


def leave_report_subtitle(record):
    env = record.env
    if record._name == "hr.in.report.wizard.leave.ledger":
        return _(
            "Lists each time off request in the selected period with type, duration, and "
            "workflow state - suitable for payroll reconciliation and leave audits."
        )
    if record._name == "hr.in.report.wizard.leave.balance":
        return _(
            "Shows allocation lines that are valid on the as-of date (gross entitlement). "
            "Use together with ledger and accrual audit for a full picture of balances."
        )
    if record._name == "hr.in.report.wizard.leave.accrual":
        return _(
            "Lists allocations created in the period - intended to verify accrual engine runs, "
            "manual top-ups, and carry-forward postings."
        )
    return ""


def leave_report_sum_keys(record):
    if record._name == "hr.in.report.wizard.leave.ledger":
        return ["days"]
    if record._name == "hr.in.report.wizard.leave.balance":
        return ["allocated"]
    if record._name == "hr.in.report.wizard.leave.accrual":
        return ["days"]
    return []


def leave_report_filter_rows(record):
    env = record.env
    rows = []
    if record._name == "hr.in.report.wizard.leave.balance":
        rows.append(
            {
                "label": _("Reference date"),
                "value": format_date(env, record.date_to),
            }
        )
    else:
        rows.append(
            {
                "label": _("Period"),
                "value": _("%(dfrom)s to %(dto)s")
                % {
                    "dfrom": format_date(env, record.date_from),
                    "dto": format_date(env, record.date_to),
                },
            }
        )
    rows.append(
        {
            "label": _("Companies"),
            "value": ", ".join(record.company_ids.mapped("name")) or "-",
        }
    )
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


def leave_report_summary_metrics(record, lines, column_keys, column_labels):
    env = record.env
    metrics = [{"label": _("Detail lines"), "value": str(len(lines))}]
    sum_keys = leave_report_sum_keys(record)
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


def leave_report_format_row_values(env, lines, column_keys):
    out = []
    for line in lines:
        out.append([_format_cell(env, line.get(k, "")) for k in column_keys])
    return out


def leave_report_column_classes(column_keys):
    right = {"days", "allocated"}
    return ["text-end" if k in right else "text-start" for k in column_keys]


def leave_report_column_meta(column_labels, column_keys):
    classes = leave_report_column_classes(column_keys)
    return [{"label": lab, "class": cls} for lab, cls in zip(column_labels, classes)]


def leave_report_table_rows(row_values, column_meta):
    rows = []
    for row in row_values:
        cells = []
        for i, val in enumerate(row):
            cls = column_meta[i]["class"] if i < len(column_meta) else "text-start"
            cells.append({"value": val, "class": cls})
        rows.append(cells)
    return rows


def enrich_leave_pdf_context(record, ctx):
    """Merge professional PDF keys; expects base ctx from hr.in.report.wizard.mixin."""
    env = record.env
    lines = ctx.get("lines") or []
    column_keys = ctx.get("column_keys") or []
    column_labels = ctx.get("column_labels") or []
    company = record.company_ids[:1] or env.company
    filter_rows = leave_report_filter_rows(record)
    summary_metrics = leave_report_summary_metrics(record, lines, column_keys, column_labels)
    row_values = leave_report_format_row_values(env, lines, column_keys)
    column_meta = leave_report_column_meta(column_labels, column_keys)
    table_rows = leave_report_table_rows(row_values, column_meta)
    prepared_on = format_datetime(env, fields.Datetime.now(), dt_format="medium")
    ctx.update(
        {
            "company": company,
            "o": record,
            "layout_document_title": ctx.get("doc_title") or "",
            "report_subtitle": leave_report_subtitle(record),
            "filter_rows": filter_rows,
            "summary_metrics": summary_metrics,
            "column_meta": column_meta,
            "table_rows": table_rows,
            "row_values": row_values,
            "section_filters_label": _("Applied filters"),
            "section_detail_label": _("Detail"),
            "section_summary_label": _("Summary"),
            "prepared_footer": _("Prepared on %(when)s · Prepared by %(who)s")
            % {"when": prepared_on, "who": env.user.display_name},
            "table_empty_message": _("No records match the selected filters."),
        }
    )
    return ctx
