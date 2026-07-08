# -*- coding: utf-8 -*-
"""
Helpers for parsing RingCentral presence webhook payloads (activeCalls).
"""
import re
from datetime import datetime, timezone


def extract_phone(value):
    """Normalize from/to whether string or dict with phoneNumber."""
    if not value:
        return ''
    if isinstance(value, dict):
        return value.get('phoneNumber') or value.get('extensionNumber') or ''
    return str(value).strip()


def is_extension_number(number):
    """True for short internal extension numbers (e.g. 101), not PSTN."""
    if not number:
        return False
    stripped = str(number).strip()
    if stripped.startswith('+'):
        return False
    digits = re.sub(r'\D', '', stripped)
    return bool(digits) and len(digits) <= 6


def is_external_pstn(number, known_extensions=None):
    """True for external PSTN phone numbers (not extensions)."""
    if not number:
        return False
    if is_extension_number(number):
        return False
    if known_extensions and str(number).strip() in known_extensions:
        return False
    stripped = str(number).strip()
    if stripped.startswith('+'):
        return True
    digits = re.sub(r'\D', '', stripped)
    return bool(digits) and len(digits) >= 10


def is_internal_agent_leg(call_leg, known_extensions=None):
    """True for RingCentral internal agent/extension legs (not business calls)."""
    if not call_leg:
        return False
    if call_leg.get('direction') != 'Inbound':
        return False
    from_number = extract_phone(call_leg.get('from'))
    if not from_number:
        return False
    if known_extensions and from_number in known_extensions:
        return True
    return is_extension_number(from_number)


def select_business_call_leg(active_calls, known_extensions=None):
    """Pick the business-meaningful call leg from presence activeCalls."""
    if not active_calls:
        return None
    known_extensions = known_extensions or []
    business_legs = [
        leg for leg in active_calls
        if not is_internal_agent_leg(leg, known_extensions)
    ]
    if not business_legs:
        return _synthesize_business_leg(active_calls, known_extensions)
    # External caller on an inbound leg → partner calling the business line
    inbound_external_caller = [
        leg for leg in business_legs
        if leg.get('direction') == 'Inbound'
        and is_external_pstn(extract_phone(leg.get('from')), known_extensions)
    ]
    if inbound_external_caller:
        return inbound_external_caller[0]
    # Our line calling an external party
    outbound_external_callee = [
        leg for leg in business_legs
        if leg.get('direction') == 'Outbound'
        and is_external_pstn(extract_phone(leg.get('to')), known_extensions)
    ]
    if outbound_external_callee:
        return outbound_external_callee[0]
    return business_legs[0]


def _synthesize_business_leg(active_calls, known_extensions=None):
    """Build a business leg when only internal agent legs are present in activeCalls."""
    known_extensions = known_extensions or []
    for leg in active_calls:
        from_number = extract_phone(leg.get('from'))
        to_number = extract_phone(leg.get('to'))
        if leg.get('direction') == 'Inbound' and is_external_pstn(from_number, known_extensions):
            return leg
        if leg.get('direction') == 'Outbound' and is_external_pstn(to_number, known_extensions):
            return leg
    for leg in active_calls:
        from_number = extract_phone(leg.get('from'))
        to_number = extract_phone(leg.get('to'))
        if is_external_pstn(from_number, known_extensions) or is_external_pstn(to_number, known_extensions):
            return leg
    return None


def map_presence_status(telephony_status, was_answered=False):
    """Map RingCentral presence telephonyStatus to ringcentral.call.history status."""
    if telephony_status == 'NoCall':
        return 'completed' if was_answered else 'no-answer'
    mapping = {
        'Ringing': 'ringing',
        'Proceeding': 'ringing',
        'Setup': 'ringing',
        'CallConnected': 'answered',
        'OnHold': 'answered',
    }
    return mapping.get(telephony_status, 'unknown')


def is_call_answered_status(status):
    """True when the call reached a connected/answered state."""
    return status in ('answered', 'completed')


def parse_rc_datetime(iso_str):
    """Parse ISO 8601 timestamp to naive UTC datetime (Odoo convention)."""
    if not iso_str or not isinstance(iso_str, str):
        return False
    try:
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    except (ValueError, TypeError):
        return False


def map_direction(rc_direction):
    """Map RingCentral direction string to Odoo selection value."""
    if rc_direction == 'Inbound':
        return 'inbound'
    if rc_direction == 'Outbound':
        return 'outbound'
    return 'outbound'


def extract_caller_name(leg):
    """Read caller display name from presence or telephony session leg fields."""
    if not leg:
        return None
    if leg.get('fromName'):
        return leg.get('fromName')
    if leg.get('callerName'):
        return leg.get('callerName')
    from_info = leg.get('from')
    if isinstance(from_info, dict):
        return from_info.get('name')
    return None


def collect_session_aliases(active_calls, body=None):
    """Collect RingCentral session identifiers from webhook legs and body.

    Primary dedup key: telephonySessionId, then numeric sessionId.
    Never uses partyId, activeCalls[].id, or telephonyStatus.
    """
    body = body or {}
    aliases = set()
    for leg in active_calls or []:
        for key in ('sessionId', 'telephonySessionId'):
            value = leg.get(key)
            if value:
                aliases.add(str(value).strip())
    for key in ('sessionId', 'telephonySessionId'):
        value = body.get(key)
        if value:
            aliases.add(str(value).strip())

    telephony_ids = sorted(alias for alias in aliases if alias.startswith('s-'))
    numeric_ids = sorted(alias for alias in aliases if not alias.startswith('s-'))

    telephony_session_id = telephony_ids[0] if telephony_ids else None
    numeric_session_id = numeric_ids[0] if numeric_ids else None
    primary_key = telephony_session_id or numeric_session_id
    canonical_id = numeric_session_id or telephony_session_id

    return {
        'primary_key': primary_key,
        'canonical_id': canonical_id,
        'telephony_session_id': telephony_session_id,
        'numeric_session_id': numeric_session_id,
        'aliases': list(aliases),
    }


def resolve_session_from_payload(body, active_calls=None):
    """Resolve stable session identifiers from a webhook payload."""
    body = body or {}
    if active_calls is None:
        active_calls = body.get('activeCalls') or []
    return collect_session_aliases(active_calls, body)
