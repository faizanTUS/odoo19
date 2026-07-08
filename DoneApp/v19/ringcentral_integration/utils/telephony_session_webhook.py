# -*- coding: utf-8 -*-
"""
Helpers for RingCentral account/extension telephony session webhooks.
"""
from odoo.addons.ringcentral_integration.utils import presence_webhook as pw_utils

SESSION_STATUS_TO_PRESENCE = {
    'Setup': 'Ringing',
    'Proceeding': 'Ringing',
    'Answered': 'CallConnected',
    'Hold': 'OnHold',
    'Disconnected': 'NoCall',
    'Gone': 'NoCall',
    'Voicemail': 'NoCall',
    'NoAnswer': 'NoCall',
}

SESSION_STATUS_TO_CALL_RESULT = {
    'Voicemail': 'missed',
    'NoAnswer': 'missed',
    'Gone': 'rejected',
}


def map_session_status_code(status_code):
    """Map telephony session party status code to presence telephonyStatus."""
    if not status_code:
        return 'unknown'
    return SESSION_STATUS_TO_PRESENCE.get(status_code, 'unknown')


def map_session_call_result(status_code):
    """Map telephony session terminal status to call_result when applicable."""
    if not status_code:
        return None
    return SESSION_STATUS_TO_CALL_RESULT.get(status_code)


def parties_to_active_calls(body):
    """Convert telephony session parties[] to presence-style activeCalls[]."""
    numeric_session_id = body.get('sessionId')
    telephony_session_id = body.get('telephonySessionId')
    session_id = numeric_session_id or telephony_session_id
    if not session_id:
        return []
    event_time = body.get('eventTime')
    active_calls = []
    for party in body.get('parties') or []:
        status_code = (party.get('status') or {}).get('code') or ''
        from_info = party.get('from') or {}
        caller_name = from_info.get('name') if isinstance(from_info, dict) else None
        active_calls.append({
            'sessionId': str(numeric_session_id or session_id),
            'telephonySessionId': (
                str(telephony_session_id) if telephony_session_id else None
            ),
            'direction': party.get('direction'),
            'from': party.get('from'),
            'to': party.get('to'),
            'telephonyStatus': map_session_status_code(status_code),
            'startTime': event_time,
            'partyId': party.get('id'),
            'extensionId': party.get('extensionId'),
            'terminationType': 'final' if status_code in ('Disconnected', 'Gone', 'Voicemail', 'NoAnswer') else None,
            'sessionStatusCode': status_code,
            'callerName': caller_name,
            'fromName': caller_name,
        })
    return active_calls


def normalize_telephony_session_payload(payload):
    """Normalize a telephony session webhook into presence-style payload."""
    body = dict(payload.get('body') or {})
    active_calls = parties_to_active_calls(body)
    if not active_calls:
        return None
    aggregated = active_calls[0].get('telephonyStatus')
    for leg in active_calls:
        if leg.get('telephonyStatus') == 'CallConnected':
            aggregated = 'CallConnected'
            break
        if leg.get('telephonyStatus') == 'Ringing' and aggregated != 'CallConnected':
            aggregated = 'Ringing'
    body['activeCalls'] = active_calls
    body.setdefault('telephonyStatus', aggregated)
    body.setdefault('aggregatedTelephonyStatus', aggregated)
    body.setdefault('extensionId', body.get('extensionId') or active_calls[0].get('extensionId'))
    return {
        **payload,
        'body': body,
    }
