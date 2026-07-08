# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Refresh webhook subscriptions to include call-log and recording event filters."""
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    configs = env['ringcentral.config'].search([
        ('active', '=', True),
        ('access_token', '!=', False),
    ])
    for config in configs:
        try:
            config.with_context(return_notification=False).create_webhook_subscription()
            _logger.info(
                'RingCentral 19.0.0.0.11: refreshed webhook subscription for config %s',
                config.id,
            )
        except Exception as error:
            _logger.warning(
                'RingCentral 19.0.0.0.11: could not refresh webhook subscription '
                'for config %s: %s',
                config.id,
                error,
            )
