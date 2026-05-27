# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
import base64
import io
from datetime import date, datetime, time as time_cls
from decimal import Decimal

import xlsxwriter


def _excel_date_num_format(env):
    """Map Odoo lang date_format (strftime-style) to an Excel num_format string."""
    if not env:
        return "yyyy-mm-dd"
    from odoo.tools import get_lang

    fmt = get_lang(env).date_format or "%Y-%m-%d"
    s = fmt.replace("%%", "\x00PERCENT\x00")
    replacements = (
        ("%Y", "yyyy"),
        ("%y", "yy"),
        ("%m", "mm"),
        ("%d", "dd"),
        ("%b", "mmm"),
        ("%B", "mmmm"),
    )
    for py, xl in replacements:
        s = s.replace(py, xl)
    return s.replace("\x00PERCENT\x00", "%")


def _coerce_cell_value(val):
    """Normalize values for Excel (avoid bool FALSE for empty dates)."""
    if val is False:
        return None
    return val


def _default_column_widths(headers, rows, max_sample=300):
    """Heuristic column widths (Excel character units), capped for readability."""
    n = len(headers)
    widths = [min(48, max(10, len(str(h)) + 2)) for h in headers]
    for row in rows[:max_sample]:
        for c, val in enumerate(row):
            if c >= n:
                break
            val = _coerce_cell_value(val)
            if val is None:
                continue
            if isinstance(val, datetime):
                cell_len = 18
            elif isinstance(val, date):
                cell_len = 14
            elif isinstance(val, Decimal):
                cell_len = 16
            elif isinstance(val, float):
                cell_len = 16
            else:
                cell_len = len(str(val))
            widths[c] = min(52, max(widths[c], cell_len + 2))
    return widths


def _merge_last_col(headers):
    """Last column index for merged title blocks (at least 8 columns wide)."""
    n = len(headers)
    return max(n - 1, 7)


def _write_professional_report_header(ws, wb, start_row, header, merge_last, env):
    """Write title, company, subtitle, filters, and section label before the detail table.

    :returns: row index where the table **column titles** row should be written.
    """
    title_fmt = wb.add_format(
        {
            "bold": True,
            "font_size": 16,
            "valign": "vcenter",
            "bottom": 2,
            "bottom_color": "#2563eb",
        }
    )
    company_fmt = wb.add_format({"bold": True, "font_size": 12, "valign": "vcenter"})
    subtitle_fmt = wb.add_format(
        {
            "italic": True,
            "text_wrap": True,
            "font_size": 10,
            "valign": "top",
        }
    )
    section_fmt = wb.add_format(
        {
            "bold": True,
            "font_size": 11,
            "bg_color": "#DEE2E6",
            "border": 1,
            "valign": "vcenter",
        }
    )
    filter_label_fmt = wb.add_format(
        {"bold": True, "text_wrap": True, "valign": "vcenter", "border": 1, "bg_color": "#F8F9FA"}
    )
    filter_value_fmt = wb.add_format({"text_wrap": True, "valign": "vcenter", "border": 1})

    r = start_row
    ws.merge_range(r, 0, r, merge_last, header.get("title") or "", title_fmt)
    ws.set_row(r, 30)
    r += 1

    company = header.get("company") or ""
    if company:
        ws.merge_range(r, 0, r, merge_last, company, company_fmt)
        ws.set_row(r, 22)
        r += 1

    subtitle = (header.get("subtitle") or "").strip()
    if subtitle:
        ws.merge_range(r, 0, r, merge_last, subtitle, subtitle_fmt)
        ws.set_row(r, 42)
        r += 1

    r += 1  # spacer before filters

    sec_filters = header.get("section_filters_label") or "Applied filters"
    ws.merge_range(r, 0, r, merge_last, sec_filters, section_fmt)
    ws.set_row(r, 22)
    r += 1

    for fr in header.get("filter_rows") or []:
        lab = fr.get("label", "")
        val = fr.get("value", "")
        if hasattr(val, "__call__"):
            val = str(val)
        else:
            val = val if val is not False and val is not None else ""
        ws.write(r, 0, lab, filter_label_fmt)
        ws.merge_range(r, 1, r, merge_last, str(val), filter_value_fmt)
        ws.set_row(r, 20)
        r += 1

    r += 1  # spacer before detail

    sec_detail = header.get("section_detail_label") or "Detail"
    ws.merge_range(r, 0, r, merge_last, sec_detail, section_fmt)
    ws.set_row(r, 22)
    r += 1

    return r


def _write_summary_block(ws, wb, start_row, header, merge_last):
    """Append summary + footer after the data block. Returns next free row."""
    r = start_row
    summary_rows = header.get("summary_rows") or []
    if not summary_rows:
        footer = (header.get("footer") or "").strip()
        if footer:
            footer_fmt = wb.add_format({"italic": True, "font_size": 9, "text_wrap": True, "valign": "top"})
            r += 1
            ws.merge_range(r, 0, r, merge_last, footer, footer_fmt)
            ws.set_row(r, 28)
            r += 1
        return r

    section_fmt = wb.add_format(
        {
            "bold": True,
            "font_size": 11,
            "bg_color": "#DEE2E6",
            "border": 1,
            "valign": "vcenter",
        }
    )
    sum_label_fmt = wb.add_format({"bold": True, "border": 1, "valign": "vcenter", "bg_color": "#F8F9FA"})
    sum_val_fmt = wb.add_format({"bold": True, "border": 1, "valign": "vcenter", "align": "right"})

    r += 1
    sec_sum = header.get("section_summary_label") or "Summary"
    ws.merge_range(r, 0, r, merge_last, sec_sum, section_fmt)
    ws.set_row(r, 22)
    r += 1
    for item in summary_rows:
        ws.write(r, 0, item.get("label", ""), sum_label_fmt)
        ws.merge_range(r, 1, r, merge_last, str(item.get("value", "")), sum_val_fmt)
        ws.set_row(r, 20)
        r += 1

    footer = (header.get("footer") or "").strip()
    if footer:
        footer_fmt = wb.add_format({"italic": True, "font_size": 9, "text_wrap": True, "valign": "top"})
        r += 1
        ws.merge_range(r, 0, r, merge_last, footer, footer_fmt)
        ws.set_row(r, 28)
        r += 1
    return r


def build_xlsx_bytes(sheet_name, headers, rows, env=None, xlsx_options=None, header=None):
    """
    Build a one-sheet XLSX.

    :param headers: list of str column titles
    :param rows: list of list/tuple aligned to headers
    :param env: optional Odoo env for locale date num_format
    :param xlsx_options: optional dict:
        - column_widths: list[float|None] widths per column (None = skip override)
        - header_row_height: float (points) for **table** header row when no report header
        - default_row_height: float
        - freeze_panes: (row, col); ignored when ``header`` is set (freeze follows detail table)
    :param header: optional dict (professional cover, PDF-aligned):
        - title, company, subtitle (str)
        - filter_rows: [{"label", "value"}, ...]
        - summary_rows: [{"label", "value"}, ...]
        - footer (str)
        - section_filters_label, section_detail_label, section_summary_label (str, optional)
    """
    xlsx_options = xlsx_options or {}
    buf = io.BytesIO()
    wb = xlsxwriter.Workbook(buf, {"in_memory": True})
    ws = wb.add_worksheet((sheet_name or "Report")[:31])

    date_num_fmt = _excel_date_num_format(env)
    date_fmt = wb.add_format({"num_format": date_num_fmt, "align": "left", "valign": "vcenter", "border": 1})
    dt_fmt = wb.add_format(
        {"num_format": date_num_fmt + " hh:mm", "align": "left", "valign": "vcenter", "border": 1}
    )
    header_fmt = wb.add_format(
        {
            "bold": True,
            "text_wrap": True,
            "valign": "vcenter",
            "align": "center",
            "bg_color": "#E9ECEF",
            "border": 1,
        }
    )
    cell_wrap_fmt = wb.add_format({"text_wrap": True, "valign": "vcenter", "border": 1})
    default_cell_fmt = wb.add_format({"valign": "vcenter", "border": 1})
    num_cell_fmt = wb.add_format({"valign": "vcenter", "border": 1, "align": "right", "num_format": "#,##0.00"})

    ncols = len(headers)
    merge_last = _merge_last_col(headers)

    if header:
        table_header_row = _write_professional_report_header(ws, wb, 0, header, merge_last, env)
    else:
        table_header_row = 0

    header_h = xlsx_options.get("header_row_height") or 24
    ws.set_row(table_header_row, header_h)
    default_rh = xlsx_options.get("default_row_height") or 20
    ws.set_default_row(default_rh)

    if header:
        ws.freeze_panes(table_header_row + 1, 0)
    else:
        freeze = xlsx_options.get("freeze_panes", (1, 0))
        if freeze:
            ws.freeze_panes(*freeze)

    for c, h in enumerate(headers):
        ws.write(table_header_row, c, h, header_fmt)

    first_data_row = table_header_row + 1
    last_data_row = table_header_row
    if not rows:
        if header and env:
            empty_fmt = wb.add_format({"italic": True, "border": 1, "valign": "vcenter", "bg_color": "#FAFAFA"})
            msg = env._("No records match the selected filters.")
            ws.merge_range(first_data_row, 0, first_data_row, merge_last, msg, empty_fmt)
            ws.set_row(first_data_row, 26)
            last_data_row = first_data_row
    else:
        for r, row in enumerate(rows, start=first_data_row):
            ws.set_row(r, default_rh)
            for c, val in enumerate(row):
                val = _coerce_cell_value(val)
                fmt = default_cell_fmt
                if val is None:
                    ws.write_blank(r, c, None, fmt)
                elif isinstance(val, datetime):
                    if val.time() != time_cls.min:
                        ws.write_datetime(r, c, val, dt_fmt)
                    else:
                        ws.write_datetime(r, c, val, date_fmt)
                elif isinstance(val, date):
                    ws.write_datetime(r, c, datetime.combine(val, time_cls.min), date_fmt)
                elif isinstance(val, float):
                    ws.write_number(r, c, val, num_cell_fmt)
                elif isinstance(val, Decimal):
                    ws.write_number(r, c, float(val), num_cell_fmt)
                elif isinstance(val, int) and not isinstance(val, bool):
                    ws.write_number(r, c, val, default_cell_fmt)
                elif isinstance(val, str) and ("\n" in val or len(val) > 40):
                    ws.write_string(r, c, val, cell_wrap_fmt)
                else:
                    ws.write(r, c, val, fmt)
        last_data_row = first_data_row + len(rows) - 1

    if header:
        next_row = last_data_row + 1
        _write_summary_block(ws, wb, next_row, header, merge_last)

    explicit = xlsx_options.get("column_widths")
    merged = _default_column_widths(headers, rows)
    if explicit:
        for i in range(ncols):
            ow = explicit[i] if i < len(explicit) else None
            if ow is not None:
                merged[i] = float(ow)
    for i, w in enumerate(merged):
        ws.set_column(i, i, w)

    wb.close()
    return buf.getvalue()


def xlsx_attachment(env, name, content_bytes):
    return env["ir.attachment"].create(
        {
            "name": name,
            "type": "binary",
            "datas": base64.b64encode(content_bytes),
            "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "res_model": False,
        }
    )
