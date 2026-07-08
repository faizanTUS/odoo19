# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Backfill telephony session ids and merge obvious duplicate call rows."""
    cr.execute("""
        UPDATE ringcentral_call_history
        SET ringcentral_telephony_session_id = ringcentral_call_id
        WHERE ringcentral_telephony_session_id IS NULL
          AND ringcentral_call_id LIKE 's-%'
    """)

    cr.execute("""
        SELECT id, config_id, ringcentral_call_id, ringcentral_telephony_session_id,
               direction, status, from_number, to_number, start_time,
               initiated_by_id, answered_by_id, user_id,
               from_partner_id, to_partner_id, recording_id,
               ringcentral_call_log_id, caller_name, end_time, duration,
               call_result, webhook_payloads
        FROM ringcentral_call_history
        WHERE ringcentral_telephony_session_id IS NOT NULL
           OR ringcentral_call_id IS NOT NULL
        ORDER BY config_id, COALESCE(ringcentral_telephony_session_id, ringcentral_call_id), start_time
    """)
    rows = cr.fetchall()
    columns = [
        'id', 'config_id', 'ringcentral_call_id', 'ringcentral_telephony_session_id',
        'direction', 'status', 'from_number', 'to_number', 'start_time',
        'initiated_by_id', 'answered_by_id', 'user_id',
        'from_partner_id', 'to_partner_id', 'recording_id',
        'ringcentral_call_log_id', 'caller_name', 'end_time', 'duration',
        'call_result', 'webhook_payloads',
    ]
    records = [dict(zip(columns, row)) for row in rows]

    def session_keys(record):
        keys = set()
        for value in (record['ringcentral_call_id'], record['ringcentral_telephony_session_id']):
            if value:
                keys.add(str(value))
        return keys

    merged_ids = set()
    by_config = {}
    for record in records:
        by_config.setdefault(record['config_id'], []).append(record)

    for config_id, config_records in by_config.items():
        groups = []
        for record in config_records:
            if record['id'] in merged_ids:
                continue
            keys = session_keys(record)
            if not keys:
                continue
            matched_group = None
            for group in groups:
                if keys & group['keys']:
                    matched_group = group
                    break
            if matched_group:
                matched_group['keys'].update(keys)
                matched_group['records'].append(record)
            else:
                groups.append({'keys': keys, 'records': [record]})

        for group in groups:
            dupes = group['records']
            if len(dupes) < 2:
                continue
            keeper = max(dupes, key=lambda r: (r['start_time'] or '', r['id']))
            for dupe in dupes:
                if dupe['id'] == keeper['id']:
                    continue
                updates = {}
                for field in (
                    'ringcentral_call_id', 'ringcentral_telephony_session_id',
                    'initiated_by_id', 'answered_by_id', 'from_partner_id',
                    'to_partner_id', 'recording_id', 'ringcentral_call_log_id',
                    'caller_name', 'end_time', 'duration', 'call_result',
                ):
                    if not keeper.get(field) and dupe.get(field):
                        updates[field] = dupe[field]
                if updates:
                    set_clause = ', '.join(f'{field} = %s' for field in updates)
                    cr.execute(
                        f'UPDATE ringcentral_call_history SET {set_clause} WHERE id = %s',
                        list(updates.values()) + [keeper['id']],
                    )
                cr.execute('DELETE FROM ringcentral_call_history WHERE id = %s', (dupe['id'],))
                merged_ids.add(dupe['id'])
                _logger.info(
                    'RingCentral 19.0.0.0.18: merged duplicate call history %s into %s (config %s)',
                    dupe['id'], keeper['id'], config_id,
                )

    _logger.info('RingCentral 19.0.0.0.18: telephony session backfill and duplicate merge complete')
