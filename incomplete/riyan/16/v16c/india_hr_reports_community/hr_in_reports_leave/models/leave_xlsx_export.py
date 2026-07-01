# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
"""XLSX layout aligned with PDF via shared hub export (title, company, filters, detail, summary)."""

import base64

from odoo import fields, _
from odoo.addons.india_hr_reports_community.hr_in_reports.models.hr_in_report_export_utils import build_xlsx_bytes, xlsx_attachment
from odoo.tools import format_datetime

from .leave_report_formatting import (
    leave_report_filter_rows,
    leave_report_subtitle,
    leave_report_summary_metrics,
)


def export_leave_xlsx_professional(record):
    """Build a structured workbook from a leave report wizard record."""
    record.ensure_one()
    record._validate_report_access()
    env = record.env
    ds = record._get_dataset()
    record._enforce_row_cap(len(ds["rows"]))
    lines = ds["rows"]
    cols = ds["columns"]
    column_keys = [c[0] for c in cols]
    column_labels = [c[1] for c in cols]
    rows_data = [[line.get(k, "") for k in column_keys] for line in lines]

    company = record.company_ids[:1] or env.company
    header = {
        "title": ds.get("title") or _("Report"),
        "company": company.display_name,
        "subtitle": leave_report_subtitle(record),
        "filter_rows": leave_report_filter_rows(record),
        "summary_rows": leave_report_summary_metrics(record, lines, column_keys, column_labels),
        "footer": _("Prepared on %(when)s - Prepared by %(who)s")
        % {
            "when": format_datetime(env, fields.Datetime.now(), dt_format="medium"),
            "who": env.user.display_name,
        },
        "section_filters_label": _("Applied filters"),
        "section_detail_label": _("Detail"),
        "section_summary_label": _("Summary"),
    }

    content = build_xlsx_bytes(
        (ds.get("sheet_name") or "report")[:31],
        column_labels,
        rows_data,
        env=env,
        xlsx_options=ds.get("xlsx_options"),
        header=header,
    )

    fname = (ds.get("filename") or "report") + ".xlsx"
    att = xlsx_attachment(env, fname, content)
    return {
        "type": "ir.actions.act_url",
        "url": "/web/content/%s?download=true" % att.id,
        "target": "self",
    }
