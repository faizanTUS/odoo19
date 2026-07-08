# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestRingCentralCallEvent(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.config = cls.env['ringcentral.config'].create({
            'name': 'Call Event Test Config',
            'client_id': 'call_event_client',
            'client_secret': 'call_event_secret',
        })
        cls.user = cls.env['res.users'].create({
            'name': 'Call Event User',
            'login': 'rc_call_event_user@test.com',
            'group_ids': [(4, cls.env.ref('ringcentral_integration.group_ringcentral_user').id)],
        })
        cls.CallHistory = cls.env['ringcentral.call.history']

    def test_outbound_start_creates_pending_record(self):
        record_id = self.CallHistory.with_user(self.user).process_call_event(
            'outbound_start',
            phone_number='+17142426520',
            direction='outbound',
        )
        self.assertTrue(record_id)
        call = self.CallHistory.browse(record_id)
        self.assertEqual(call.initiated_by_id, self.user)
        self.assertEqual(call.user_id, self.user)
        self.assertEqual(call.direction, 'outbound')
        self.assertEqual(call.to_number, '+17142426520')
        self.assertEqual(call.status, 'initiated')

    def test_outbound_start_dedupes_recent_pending(self):
        CallHistory = self.CallHistory.with_user(self.user)
        first_id = CallHistory.process_call_event(
            'outbound_start',
            phone_number='+17142426520',
        )
        second_id = CallHistory.process_call_event(
            'outbound_start',
            phone_number='+17142426520',
        )
        self.assertEqual(first_id, second_id)
        self.assertEqual(self.CallHistory.search_count([
            ('to_number', '=', '+17142426520'),
            ('initiated_by_id', '=', self.user.id),
        ]), 1)

    def test_outbound_merge_with_webhook_session(self):
        record_id = self.CallHistory.with_user(self.user).process_call_event(
            'outbound_start',
            phone_number='+17142426520',
        )
        pending = self.CallHistory.browse(record_id)
        self.assertFalse(pending.ringcentral_call_id)

        from odoo.addons.ringcentral_integration.tests.test_presence_webhook import (
            _outbound_ringing_payload,
            SESSION_ID,
        )
        self.CallHistory.process_presence_webhook(self.config, _outbound_ringing_payload())
        call = self.CallHistory.search([
            ('ringcentral_call_id', '=', SESSION_ID),
            ('config_id', '=', self.config.id),
        ], limit=1)
        self.assertTrue(call)
        self.assertEqual(call.id, pending.id)
        self.assertEqual(call.initiated_by_id, self.user)

    def test_inbound_ring_updates_existing_webhook_record(self):
        from odoo.addons.ringcentral_integration.tests.test_presence_webhook import (
            _inbound_external_ringing_payload,
        )
        self.env['res.partner'].create({
            'name': 'Inbound Caller',
            'phone': '+17145550123',
        })
        self.CallHistory.process_presence_webhook(
            self.config,
            {
                **_inbound_external_ringing_payload(),
                'body': {
                    **_inbound_external_ringing_payload()['body'],
                    'activeCalls': [{
                        'direction': 'Inbound',
                        'from': '+17145550123',
                        'to': '+17144927516',
                        'telephonyStatus': 'Ringing',
                        'sessionId': 'inbound-session-1',
                        'startTime': '2026-06-11T08:00:00.000Z',
                    }],
                },
            },
        )
        record_id = self.CallHistory.with_user(self.user).process_call_event(
            'inbound_ring',
            phone_number='+17145550123',
            session_id='inbound-session-1',
            direction='inbound',
            caller_name='Inbound Caller',
        )
        self.assertTrue(record_id)
        call = self.CallHistory.browse(record_id)
        self.assertEqual(call.direction, 'inbound')
        self.assertEqual(call.status, 'ringing')
        self.assertEqual(call.from_number, '+17145550123')
        self.assertEqual(call.ringcentral_call_id, 'inbound-session-1')
        self.assertEqual(call.caller_name, 'Inbound Caller')
        self.assertEqual(call.answered_by_id, self.user)

    def test_inbound_ring_bootstrap_creates_when_webhook_missing(self):
        record_id = self.CallHistory.with_user(self.user).process_call_event(
            'inbound_ring',
            phone_number='+17145550999',
            session_id='bootstrap-session-1',
            direction='inbound',
            caller_name='Bootstrap Caller',
        )
        self.assertTrue(record_id)
        call = self.CallHistory.browse(record_id)
        self.assertEqual(call.direction, 'inbound')
        self.assertEqual(call.status, 'ringing')
        self.assertEqual(call.from_number, '+17145550999')
        self.assertEqual(call.ringcentral_call_id, 'bootstrap-session-1')

    def test_inbound_ring_bootstrap_creates_with_phone_only(self):
        record_id = self.CallHistory.with_user(self.user).process_call_event(
            'inbound_ring',
            phone_number='+17145550998',
            direction='inbound',
        )
        self.assertTrue(record_id)
        self.assertEqual(self.CallHistory.browse(record_id).from_number, '+17145550998')

    def test_inbound_ring_without_session_or_phone_does_not_create(self):
        before = self.CallHistory.search_count([('config_id', '=', self.config.id)])
        record_id = self.CallHistory.with_user(self.user).process_call_event(
            'inbound_ring',
            direction='inbound',
        )
        self.assertFalse(record_id)
        self.assertEqual(
            self.CallHistory.search_count([('config_id', '=', self.config.id)]),
            before,
        )

    def test_inbound_ring_bootstrap_then_webhook_single_record(self):
        from odoo.addons.ringcentral_integration.tests.test_presence_webhook import (
            _inbound_external_ringing_payload,
        )
        self.env['res.partner'].create({
            'name': 'Merge Caller',
            'phone': '+17145550177',
        })
        bootstrap_id = self.CallHistory.with_user(self.user).process_call_event(
            'inbound_ring',
            phone_number='+17145550177',
            session_id='merge-session-1',
            direction='inbound',
        )
        payload = {
            **_inbound_external_ringing_payload(),
            'body': {
                **_inbound_external_ringing_payload()['body'],
                'activeCalls': [{
                    'direction': 'Inbound',
                    'from': '+17145550177',
                    'to': '+17144927516',
                    'telephonyStatus': 'Ringing',
                    'sessionId': 'merge-session-1',
                    'startTime': '2026-06-11T08:00:00.000Z',
                }],
            },
        }
        self.CallHistory.process_presence_webhook(self.config, payload)
        calls = self.CallHistory.search([
            ('config_id', '=', self.config.id),
            ('ringcentral_call_id', '=', 'merge-session-1'),
        ])
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls.id, bootstrap_id)
        self.assertEqual(calls.to_number, '+17144927516')

    def test_outbound_bootstrap_merges_with_telephony_session_webhook(self):
        """Widget outbound bootstrap merges when webhook arrives with telephony session id."""
        from odoo.addons.ringcentral_integration.tests.test_presence_webhook import (
            TELEPHONY_SESSION_ID,
            SESSION_ID,
            _outbound_ringing_payload,
        )
        bootstrap_id = self.CallHistory.with_user(self.user).process_call_event(
            'outbound_start',
            phone_number='+17142426520',
            session_id=TELEPHONY_SESSION_ID,
        )
        self.assertTrue(bootstrap_id)
        self.CallHistory.process_presence_webhook(self.config, _outbound_ringing_payload())
        calls = self.CallHistory.search([
            ('config_id', '=', self.config.id),
            '|',
            ('ringcentral_call_id', '=', SESSION_ID),
            ('ringcentral_telephony_session_id', '=', TELEPHONY_SESSION_ID),
        ])
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls.id, bootstrap_id)
        self.assertEqual(calls.ringcentral_call_id, SESSION_ID)

    def test_inbound_rejected_creates_bootstrap_when_missing(self):
        reject_id = self.CallHistory.with_user(self.user).process_call_event(
            'inbound_rejected',
            phone_number='+17145550125',
            session_id='reject-bootstrap-1',
            direction='inbound',
        )
        self.assertTrue(reject_id)
        call = self.CallHistory.browse(reject_id)
        self.assertEqual(call.status, 'no-answer')
        self.assertEqual(call.call_result, 'rejected')
        self.assertEqual(call.ringcentral_call_id, 'reject-bootstrap-1')

    def test_inbound_rejected_updates_call_result(self):
        self.env['res.partner'].create({
            'name': 'Reject Caller',
            'phone': '+17145550124',
        })
        self.CallHistory.process_presence_webhook(self.config, {
            'uuid': 'reject-webhook-1',
            'event': '/restapi/v1.0/account/2399766010/extension/2399766010/presence',
            'timestamp': '2026-06-11T08:00:00.000Z',
            'body': {
                'telephonyStatus': 'Ringing',
                'activeCalls': [{
                    'direction': 'Inbound',
                    'from': '+17145550124',
                    'to': '+17144927516',
                    'telephonyStatus': 'Ringing',
                    'sessionId': 'inbound-session-2',
                    'startTime': '2026-06-11T08:00:00.000Z',
                }],
                'sequence': 1,
                'aggregatedTelephonyStatus': 'Ringing',
            },
        })
        record_id = self.CallHistory.with_user(self.user).process_call_event(
            'inbound_ring',
            phone_number='+17145550124',
            session_id='inbound-session-2',
            direction='inbound',
        )
        self.assertTrue(record_id)
        reject_id = self.CallHistory.with_user(self.user).process_call_event(
            'inbound_rejected',
            phone_number='+17145550124',
            session_id='inbound-session-2',
            direction='inbound',
        )
        self.assertEqual(record_id, reject_id)
        call = self.CallHistory.browse(record_id)
        self.assertEqual(call.status, 'no-answer')
        self.assertEqual(call.call_result, 'rejected')

    def test_inbound_bootstrap_phone_only_merged_by_webhook(self):
        """Widget bootstrap without session_id merges when webhook arrives."""
        bootstrap_id = self.CallHistory.with_user(self.user).process_call_event(
            'inbound_ring',
            phone_number='+17145550200',
            direction='inbound',
        )
        self.assertTrue(bootstrap_id)
        bootstrap = self.CallHistory.browse(bootstrap_id)
        self.assertFalse(bootstrap.ringcentral_call_id)
        self.assertEqual(bootstrap.to_number, 'unknown')

        self.CallHistory.process_presence_webhook(self.config, {
            'uuid': 'phone-only-merge-1',
            'event': '/restapi/v1.0/account/2399766010/extension/2399766010/presence',
            'timestamp': '2026-06-11T08:10:00.000Z',
            'body': {
                'telephonyStatus': 'Ringing',
                'activeCalls': [{
                    'direction': 'Inbound',
                    'from': '+17145550200',
                    'to': '+17144927516',
                    'telephonyStatus': 'Ringing',
                    'sessionId': 'phone-only-session-1',
                    'startTime': '2026-06-11T08:10:00.000Z',
                }],
                'sequence': 1,
                'aggregatedTelephonyStatus': 'Ringing',
            },
        })
        calls = self.CallHistory.search([
            ('config_id', '=', self.config.id),
            ('from_number', 'ilike', '7145550200'),
        ])
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls.id, bootstrap_id)
        self.assertEqual(calls.ringcentral_call_id, 'phone-only-session-1')
        self.assertEqual(calls.to_number, '+17144927516')

    def test_inbound_bootstrap_normalized_phone_merge(self):
        """Bootstrap with local format merges webhook with E.164 caller number."""
        bootstrap_id = self.CallHistory.with_user(self.user).process_call_event(
            'inbound_ring',
            phone_number='7142426520',
            direction='inbound',
        )
        self.assertTrue(bootstrap_id)

        self.CallHistory.process_presence_webhook(self.config, {
            'uuid': 'normalized-merge-1',
            'event': '/restapi/v1.0/account/2399766010/extension/2399766010/presence',
            'timestamp': '2026-06-11T08:11:00.000Z',
            'body': {
                'telephonyStatus': 'Ringing',
                'activeCalls': [{
                    'direction': 'Inbound',
                    'from': '+17142426520',
                    'to': '+17144927516',
                    'telephonyStatus': 'Ringing',
                    'sessionId': 'normalized-session-1',
                    'startTime': '2026-06-11T08:11:00.000Z',
                }],
                'sequence': 1,
                'aggregatedTelephonyStatus': 'Ringing',
            },
        })
        calls = self.CallHistory.search([
            ('config_id', '=', self.config.id),
            ('ringcentral_call_id', '=', 'normalized-session-1'),
        ])
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls.id, bootstrap_id)
