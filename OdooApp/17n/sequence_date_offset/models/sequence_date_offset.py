# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
import re
from datetime import datetime, timedelta

import pytz

from odoo import fields


DEFAULT_SEQUENCE_DIRECTIVES = {
    "year": "%Y",
    "month": "%m",
    "day": "%d",
    "y": "%y",
    "doy": "%j",
    "woy": "%W",
    "weekday": "%w",
    "h24": "%H",
    "h12": "%I",
    "min": "%M",
    "sec": "%S",
}

OFFSET_DIRECTIVE_PATTERN = re.compile(
    r"%\((?P<scope>current_|range_)?(?P<token>year|y|month|day)(?P<offset>[+-]\d+)\)s"
)


def get_interpolation_dates(env, date=None, date_range=None):
    now = range_date_value = effective_date = datetime.now(
        pytz.timezone(env.context.get("tz") or "UTC")
    )
    if date or env.context.get("ir_sequence_date"):
        effective_date = fields.Datetime.from_string(date or env.context.get("ir_sequence_date"))
    if date_range or env.context.get("ir_sequence_date_range"):
        range_date_value = fields.Datetime.from_string(
            date_range or env.context.get("ir_sequence_date_range")
        )
    return {
        "": effective_date,
        "range_": range_date_value,
        "current_": now,
    }


def get_default_interpolation_values(interpolation_dates):
    values = {}
    for scope, base_date in interpolation_dates.items():
        for key, directive in DEFAULT_SEQUENCE_DIRECTIVES.items():
            values[f"{scope}{key}"] = base_date.strftime(directive)
    return values


def get_offset_value(base_date, token, offset):
    if token == "year":
        return f"{base_date.year + offset:04d}"
    if token == "y":
        return f"{(base_date.year + offset) % 100:02d}"
    if token == "month":
        return f"{(base_date.month - 1 + offset) % 12 + 1:02d}"
    if token == "day":
        return (base_date + timedelta(days=offset)).strftime("%d")
    raise KeyError(token)


def get_offset_interpolation_values(templates, interpolation_dates):
    values = {}
    for template in filter(None, templates):
        for match in OFFSET_DIRECTIVE_PATTERN.finditer(template):
            scope = match.group("scope") or ""
            token = match.group("token")
            offset = int(match.group("offset"))
            key = f"{scope}{token}{match.group('offset')}"
            values[key] = get_offset_value(interpolation_dates[scope], token, offset)
    return values


def get_interpolation_values(env, templates, date=None, date_range=None):
    interpolation_dates = get_interpolation_dates(env, date=date, date_range=date_range)
    values = get_default_interpolation_values(interpolation_dates)
    values.update(get_offset_interpolation_values(templates, interpolation_dates))
    return values
