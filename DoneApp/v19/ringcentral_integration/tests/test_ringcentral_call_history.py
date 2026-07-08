# -*- coding: utf-8 -*-

from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestRingCentralCallHistory(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.CallHistory = cls.env['ringcentral.call.history']
        cls.config = cls.env['ringcentral.config'].create({
            'name': 'Call History Test Config',
            'client_id': 'ch_client',
            'client_secret': 'ch_secret',
        })

    def test_call_result_from_status(self):
        self.assertEqual(
            self.CallHistory._map_call_result_from_status('completed'),
            'answered',
        )
        self.assertEqual(
            self.CallHistory._map_call_result_from_status('no-answer'),
            'missed',
        )
        self.assertEqual(
            self.CallHistory._map_call_result_from_status('failed'),
            'failed',
        )
        self.assertEqual(
            self.CallHistory._map_call_result_from_status('completed', 'transfer'),
            'transferred',
        )

    def test_sync_from_call_log_dedupe(self):
        log_record = {
            'id': 'log-100',
            'sessionId': 'session-100',
            'direction': 'Inbound',
            'from': {'phoneNumber': '+15551234001'},
            'to': {'phoneNumber': '+15551234002'},
            'startTime': fields.Datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'duration': 45,
            'result': 'Accepted',
        }
        action1, record1 = self.CallHistory.sync_from_call_log_record(self.config, log_record)
        self.assertEqual(action1, 'created')
        action2, record2 = self.CallHistory.sync_from_call_log_record(self.config, log_record)
        self.assertEqual(action2, 'updated')
        self.assertEqual(record1, record2)
        self.assertEqual(record2.call_result, 'answered')

    def test_presence_webhook_sets_call_result_on_complete(self):
        payload = {
            'uuid': 'complete-uuid',
            'timestamp': '2026-06-15T10:00:00.000Z',
            'body': {
                'telephonyStatus': 'NoCall',
                'activeCalls': [{
                    'direction': 'Inbound',
                    'from': '+15559876543',
                    'to': '+15551112222',
                    'telephonyStatus': 'NoCall',
                    'sessionId': 'presence-complete-1',
                    'startTime': '2026-06-15T09:59:00.000Z',
                    'terminationType': 'final',
                }],
                'sequence': 1,
                'aggregatedTelephonyStatus': 'NoCall',
            },
        }
        self.CallHistory.process_presence_webhook(self.config, payload)
        call = self.CallHistory.search([
            ('ringcentral_call_id', '=', 'presence-complete-1'),
        ], limit=1)
        self.assertTrue(call)
        self.assertEqual(call.direction, 'inbound')
        self.assertTrue(call.end_time)

    def test_sync_updates_outbound_bootstrap_without_session(self):
        user = self.env['res.users'].create({
            'name': 'Sync Outbound User',
            'login': 'sync_outbound@test.com',
            'group_ids': [(4, self.env.ref('ringcentral_integration.group_ringcentral_user').id)],
        })
        bootstrap_id = self.CallHistory.with_user(user).process_call_event(
            'outbound_start',
            phone_number='+17142426520',
        )
        self.assertTrue(bootstrap_id)
        bootstrap = self.CallHistory.browse(bootstrap_id)
        self.assertFalse(bootstrap.ringcentral_call_id)

        start_time = fields.Datetime.now()
        log_record = {
            'id': 'log-outbound-1',
            'sessionId': 'session-outbound-1',
            'telephonySessionId': 's-session-outbound-1',
            'direction': 'Outbound',
            'from': {'phoneNumber': '+17144927516'},
            'to': {'phoneNumber': '+17142426520'},
            'startTime': start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'duration': 30,
            'result': 'Accepted',
        }
        action, synced = self.CallHistory.sync_from_call_log_record(self.config, log_record)
        self.assertEqual(action, 'updated')
        self.assertEqual(synced.id, bootstrap_id)
        self.assertEqual(synced.ringcentral_call_id, 'session-outbound-1')
        self.assertEqual(synced.ringcentral_telephony_session_id, 's-session-outbound-1')
        self.assertEqual(synced.direction, 'outbound')
        self.assertEqual(synced.initiated_by_id, user)
        self.assertEqual(synced.duration, 30)

    def test_sync_dedupes_existing_webhook_outbound_record(self):
        from odoo.addons.ringcentral_integration.tests.test_presence_webhook import (
            SESSION_ID,
            TELEPHONY_SESSION_ID,
            _outbound_ringing_payload,
        )
        self.env['res.partner'].create({
            'name': 'Sync Outbound Target',
            'phone': '+17142426520',
        })
        self.CallHistory.process_presence_webhook(self.config, _outbound_ringing_payload())
        webhook_call = self.CallHistory.search([
            ('ringcentral_call_id', '=', SESSION_ID),
        ], limit=1)
        self.assertTrue(webhook_call)

        log_record = {
            'id': 'log-outbound-2',
            'sessionId': SESSION_ID,
            'telephonySessionId': TELEPHONY_SESSION_ID,
            'direction': 'Outbound',
            'from': {'phoneNumber': '+17144927516'},
            'to': {'phoneNumber': '+17142426520'},
            'startTime': '2026-06-11T07:35:23.532Z',
            'duration': 25,
            'result': 'Accepted',
            'recording': {'id': 'rec-sync-1'},
        }
        action, synced = self.CallHistory.sync_from_call_log_record(self.config, log_record)
        self.assertEqual(action, 'updated')
        self.assertEqual(synced.id, webhook_call.id)
        self.assertEqual(synced.recording_id, 'rec-sync-1')
        self.assertEqual(
            self.CallHistory.search_count([
                ('config_id', '=', self.config.id),
                '|',
                ('ringcentral_call_id', '=', SESSION_ID),
                ('ringcentral_telephony_session_id', '=', TELEPHONY_SESSION_ID),
            ]),
            1,
        )

    def test_call_log_sync_different_sessions_same_number(self):
        """Call-log sync must not merge different sessions that share the same phone."""
        shared_caller = '+15551234001'
        start_time = fields.Datetime.now()
        log_a = {
            'id': 'log-session-a',
            'sessionId': 'sync-session-a',
            'direction': 'Inbound',
            'from': {'phoneNumber': shared_caller},
            'to': {'phoneNumber': '+15551234002'},
            'startTime': start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'duration': 30,
            'result': 'Accepted',
        }
        log_b = {
            'id': 'log-session-b',
            'sessionId': 'sync-session-b',
            'direction': 'Inbound',
            'from': {'phoneNumber': shared_caller},
            'to': {'phoneNumber': '+15551234002'},
            'startTime': start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'duration': 45,
            'result': 'Accepted',
        }
        action_a, record_a = self.CallHistory.sync_from_call_log_record(self.config, log_a)
        action_b, record_b = self.CallHistory.sync_from_call_log_record(self.config, log_b)
        self.assertEqual(action_a, 'created')
        self.assertEqual(action_b, 'created')
        self.assertNotEqual(record_a, record_b)
        self.assertEqual(record_a.ringcentral_call_id, 'sync-session-a')
        self.assertEqual(record_b.ringcentral_call_id, 'sync-session-b')
