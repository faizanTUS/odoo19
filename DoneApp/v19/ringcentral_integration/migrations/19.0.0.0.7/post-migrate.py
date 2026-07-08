# -*- coding: utf-8 -*-


def migrate(cr, version):
    """Backfill call_result from existing status values."""
    cr.execute("""
        UPDATE ringcentral_call_history
           SET call_result = CASE
               WHEN status IN ('completed', 'answered') THEN 'answered'
               WHEN status IN ('no-answer', 'busy') THEN 'missed'
               WHEN status = 'failed' THEN 'failed'
               ELSE NULL
           END
         WHERE call_result IS NULL
           AND status IS NOT NULL
    """)
