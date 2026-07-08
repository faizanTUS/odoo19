# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Populate company_ids from legacy company_id on ringcentral.config."""
    cr.execute(
        """
        INSERT INTO ringcentral_config_company_rel (config_id, company_id)
        SELECT rc.id, rc.company_id
        FROM ringcentral_config rc
        WHERE rc.company_id IS NOT NULL
          AND NOT EXISTS (
              SELECT 1
              FROM ringcentral_config_company_rel rel
              WHERE rel.config_id = rc.id
                AND rel.company_id = rc.company_id
          )
        """
    )
    _logger.info(
        'RingCentral migration 19.0.0.0.5: copied company_id into company_ids for %s config(s)',
        cr.rowcount,
    )
