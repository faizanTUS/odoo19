# -*- coding: utf-8 -*-
"""
Shared phone number normalization and variant generation for RingCentral modules.
Used by call history (partner linking) and lead creation (lead lookup by caller number)
so matching is consistent across the integration.
"""
import re


def normalize_phone(phone):
    """Normalize phone to digits only for comparison."""
    if not phone:
        return ''
    return re.sub(r'\D', '', str(phone))


def normalize_phone_number(phone, env=None):
    """Normalize phone using Odoo partner utilities when env is provided."""
    if not phone:
        return ''
    if env is not None:
        partner_model = env['res.partner']
        normalize = getattr(partner_model, '_phone_normalize', None)
        if callable(normalize):
            try:
                normalized = normalize(phone)
                if normalized:
                    return re.sub(r'\D', '', normalized)
            except Exception:
                pass
    return re.sub(r'\D', '', str(phone))


def get_last10(digits):
    """Return the last 10 digits (NANP local number) when long enough."""
    if not digits:
        return ''
    return digits[-10:] if len(digits) >= 10 else digits


def get_phone_ilike_patterns(number):
    """Build ilike patterns that match formatted CRM phones for a webhook number.

    ``+17142426520`` and ``+1 714-242-6520`` must resolve to the same patterns.
    """
    digits = normalize_phone(number)
    if not digits:
        return []

    patterns = {number, digits, f'+{digits}'}
    last10 = get_last10(digits)
    if last10:
        patterns.add(last10)
        if len(last10) == 10:
            area, exchange, line = last10[:3], last10[3:6], last10[6:]
            patterns.update({
                f'{area}-{exchange}-{line}',
                f'{area} {exchange} {line}',
                f'({area}) {exchange}-{line}',
                f'+1 {area}-{exchange}-{line}',
                f'+1 {area} {exchange} {line}',
                f'+1-{area}-{exchange}-{line}',
                f'+1 ({area}) {exchange}-{line}',
            })
    return [p for p in patterns if p]


def get_phone_variants(number, env=None):
    """Generate all variants of a phone number for matching (exact and ilike)."""
    if not number:
        return []
    variants = set(get_phone_ilike_patterns(number))
    digits_only = normalize_phone(number)
    if digits_only:
        variants.add(digits_only)
        variants.add('+' + digits_only)
        last10 = get_last10(digits_only)
        if last10:
            variants.add(last10)
    normalized = normalize_phone_number(number, env)
    if normalized:
        variants.add(normalized)
        last10 = get_last10(normalized)
        if last10:
            variants.add(last10)
    return list(variants)


def phones_match(number_a, number_b, env=None):
    """Return True when two phone numbers refer to the same line (digits + last-10)."""
    if not number_a or not number_b:
        return False
    a = normalize_phone_number(number_a, env) or normalize_phone(number_a)
    b = normalize_phone_number(number_b, env) or normalize_phone(number_b)
    if not a or not b:
        return False
    if a == b:
        return True
    last10_a = get_last10(a)
    last10_b = get_last10(b)
    return bool(last10_a and last10_b and last10_a == last10_b)


def partner_phone_fields(partner_model):
    """Return phone/mobile field names available on res.partner."""
    fields = []
    for name in ('phone', 'mobile'):
        if name in partner_model._fields:
            fields.append(name)
    return fields


def partner_sanitized_fields(partner_model):
    """Return sanitized phone field names available on res.partner."""
    fields = []
    for name in ('phone_sanitized', 'mobile_sanitized'):
        if name in partner_model._fields:
            fields.append(name)
    return fields


def build_partner_phone_domain(number, partner_model):
    """Build an OR domain to find partner candidates for a webhook phone number."""
    clauses = []
    digits = normalize_phone(number)
    if not digits:
        return []

    for field in partner_sanitized_fields(partner_model):
        clauses.append((field, '=', digits))
        last10 = get_last10(digits)
        if last10 and last10 != digits:
            clauses.append((field, '=', last10))

    for field in partner_phone_fields(partner_model):
        for pattern in get_phone_ilike_patterns(number):
            clauses.append((field, 'ilike', pattern))

    if not clauses:
        return []
    if len(clauses) == 1:
        return [clauses[0]]
    return ['|'] * (len(clauses) - 1) + clauses


def partner_matches_phone(partner, number, env=None):
    """True when any phone/mobile value on partner matches the given number."""
    if not partner or not number:
        return False
    partner_model = partner.env['res.partner']
    for field in partner_phone_fields(partner_model):
        value = getattr(partner, field, None)
        if value and phones_match(value, number, env):
            return True
    return False
