# -*- coding: utf-8 -*-
import json
import logging

_logger = logging.getLogger(__name__)


def _payload_richness(call):
    """Score a call history row for deduplication keep-winner selection."""
    payloads = call.get('webhook_payloads') or []
    if isinstance(payloads, str):
        try:
            payloads = json.loads(payloads)
        except (TypeError, ValueError):
            payloads = []
    score = len(payloads) if isinstance(payloads, list) else 0
    score += (call.get('last_webhook_sequence') or 0) * 0.001
    if call.get('recording_id'):
        score += 10
    if call.get('answered_by_id') or call.get('initiated_by_id'):
        score += 5
    return score


def migrate(cr, version):
    """Deduplicate call history rows sharing the same config + session id."""
    cr.execute("""
        SELECT config_id, ringcentral_call_id, array_agg(id ORDER BY id)
        FROM ringcentral_call_history
        WHERE ringcentral_call_id IS NOT NULL
          AND ringcentral_call_id != ''
        GROUP BY config_id, ringcentral_call_id
        HAVING COUNT(*) > 1
    """)
    duplicate_groups = cr.fetchall()
    if not duplicate_groups:
        _logger.info('RingCentral 19.0.0.0.13: no duplicate call history rows to merge')
        return

    for config_id, session_id, record_ids in duplicate_groups:
        cr.execute("""
            SELECT id, webhook_payloads, last_webhook_sequence, recording_id,
                   answered_by_id, initiated_by_id, ringcentral_telephony_session_id
            FROM ringcentral_call_history
            WHERE id = ANY(%s)
        """, (record_ids,))
        rows = cr.dictfetchall()
        if not rows:
            continue

        keeper = max(rows, key=_payload_richness)
        keeper_id = keeper['id']
        delete_ids = [row['id'] for row in rows if row['id'] != keeper_id]
        telephony_session_id = keeper.get('ringcentral_telephony_session_id')
        for row in rows:
            if row.get('ringcentral_telephony_session_id') and not telephony_session_id:
                telephony_session_id = row['ringcentral_telephony_session_id']

        if telephony_session_id and not keeper.get('ringcentral_telephony_session_id'):
            cr.execute("""
                UPDATE ringcentral_call_history
                SET ringcentral_telephony_session_id = %s
                WHERE id = %s
            """, (telephony_session_id, keeper_id))

        if delete_ids:
            cr.execute(
                "DELETE FROM ringcentral_call_history WHERE id = ANY(%s)",
                (delete_ids,),
            )
            _logger.info(
                'RingCentral 19.0.0.0.13: merged %d duplicate rows for config %s session %s into id %s',
                len(delete_ids), config_id, session_id, keeper_id,
            )
