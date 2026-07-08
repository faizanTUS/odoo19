# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Ensure agent tracking columns exist and backfill from legacy user_id."""
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
    cr.execute("""
        UPDATE ringcentral_call_history
        SET initiated_by_id = user_id
        WHERE user_id IS NOT NULL
          AND initiated_by_id IS NULL
          AND direction = 'outbound'
    """)
    cr.execute("""
        UPDATE ringcentral_call_history
        SET answered_by_id = user_id
        WHERE user_id IS NOT NULL
          AND answered_by_id IS NULL
          AND direction = 'inbound'
    """)
    cr.execute("""
        UPDATE ringcentral_call_history
        SET initiated_by_id = user_id
        WHERE user_id IS NOT NULL
          AND initiated_by_id IS NULL
          AND answered_by_id IS NULL
    """)
    _logger.info('RingCentral 19.0.0.0.8: agent tracking columns ready')
