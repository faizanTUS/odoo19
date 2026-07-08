# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Ensure agent columns exist (safety net if 19.0.0.0.8 migration was skipped)."""
    cr.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'ringcentral_call_history'
          AND column_name IN ('initiated_by_id', 'answered_by_id')
    """)
    existing = {row[0] for row in cr.fetchall()}
    if 'initiated_by_id' not in existing:
        cr.execute("""
            ALTER TABLE ringcentral_call_history
            ADD COLUMN initiated_by_id integer REFERENCES res_users(id) ON DELETE SET NULL
        """)
    if 'answered_by_id' not in existing:
        cr.execute("""
            ALTER TABLE ringcentral_call_history
            ADD COLUMN answered_by_id integer REFERENCES res_users(id) ON DELETE SET NULL
        """)
    _logger.info(
        'RingCentral 19.0.0.0.9: re-create webhook subscription from RingCentral config '
        'to enable account telephony session events.'
    )
