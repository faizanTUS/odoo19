# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.ringcentral_integration.models.ringcentral_config import (
    RC_FILTER_ACCOUNT_TELEPHONY,
    RC_FILTER_EXTENSION_TELEPHONY,
    RC_FILTER_PRESENCE,
    RingCentralRateLimitError,
    WEBHOOK_MAX_EXPIRES_IN,
)
from odoo import fields


@tagged('post_install', '-at_install')
class TestRingCentralConfigSubscription(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.config = cls.env['ringcentral.config'].create({
            'name': 'Subscription Test Config',
            'client_id': 'sub_test_client',
            'client_secret': 'sub_test_secret',
        })
        cls.Config = cls.env['ringcentral.config']

    def test_webhook_event_filters_exclude_recording_wildcard(self):
        filters = self.config._get_webhook_event_filters()
        self.assertIn(RC_FILTER_PRESENCE, filters)
        self.assertTrue(any('telephony/sessions' in item for item in filters))
        self.assertFalse(any('/recording/' in item for item in filters))

    def test_webhook_filter_sets_fallback_order(self):
        sets = self.config._get_webhook_event_filter_sets()
        self.assertEqual(len(sets), 3)
        self.assertEqual(sets[0], [RC_FILTER_PRESENCE, RC_FILTER_ACCOUNT_TELEPHONY])
        self.assertEqual(sets[1], [RC_FILTER_PRESENCE, RC_FILTER_EXTENSION_TELEPHONY])
        self.assertEqual(sets[2], [RC_FILTER_PRESENCE])

    def test_build_payload_uses_webhook_max_expires(self):
        payload = self.config._build_webhook_subscription_payload()
        self.assertEqual(payload['expiresIn'], WEBHOOK_MAX_EXPIRES_IN)
        self.assertEqual(payload['deliveryMode']['transportType'], 'WebHook')
        self.assertIn('/ringcentral/webhook/', payload['deliveryMode']['address'])

    def test_is_event_filters_api_error(self):
        self.assertTrue(self.Config._is_event_filters_api_error(
            UserError('RingCentral API request failed: Parameter [eventFilters] value is invalid'),
        ))
        self.assertFalse(self.Config._is_event_filters_api_error(
            UserError('RingCentral API request failed: address is not reachable'),
        ))

    def test_resilient_subscription_falls_back_on_invalid_filters(self):
        calls = []

        def fake_api(method, endpoint, data=None):
            calls.append(list(data.get('eventFilters', [])))
            if len(data.get('eventFilters', [])) > 1:
                raise UserError('Parameter [eventFilters] value is invalid')
            return {
                'id': 'sub-fallback-1',
                'expiresIn': WEBHOOK_MAX_EXPIRES_IN,
                'eventFilters': data['eventFilters'],
            }

        self.config._create_or_update_subscription = lambda data: fake_api('POST', '/subscription', data)
        result = self.config._create_or_update_subscription_resilient(
            self.config._build_webhook_subscription_payload(),
        )
        self.assertEqual(result['id'], 'sub-fallback-1')
        self.assertEqual(calls[0], [RC_FILTER_PRESENCE, RC_FILTER_ACCOUNT_TELEPHONY])
        self.assertEqual(calls[-1], [RC_FILTER_PRESENCE])

    def test_create_webhook_subscription_raises_user_error_when_rate_limited(self):
        self.config.write({
            'access_token': 'test-token',
            'token_expires_at': fields.Datetime.now() + timedelta(hours=1),
            'api_rate_limit_until': fields.Datetime.now() + timedelta(minutes=10),
        })
        with self.assertRaises(UserError) as ctx:
            self.config.create_webhook_subscription()
        self.assertIn('rate limit', str(ctx.exception).lower())
        self.assertNotIsInstance(ctx.exception, RingCentralRateLimitError)

    def test_sync_call_history_raises_user_error_when_rate_limited(self):
        self.config.write({
            'access_token': 'test-token',
            'token_expires_at': fields.Datetime.now() + timedelta(hours=1),
            'api_rate_limit_until': fields.Datetime.now() + timedelta(minutes=10),
        })
        with self.assertRaises(UserError) as ctx:
            self.config.sync_call_history()
        self.assertIn('rate limit', str(ctx.exception).lower())
        self.assertNotIsInstance(ctx.exception, RingCentralRateLimitError)
