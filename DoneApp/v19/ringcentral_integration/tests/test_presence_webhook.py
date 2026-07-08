# -*- coding: utf-8 -*-
import unittest

from odoo import fields
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.ringcentral_integration.utils import presence_webhook as pw_utils

TELEPHONY_SESSION_ID = 's-a786c452970f2z19eb59b7075z15521780000'
SESSION_ID = '3397577932011'
EVENT_PATH = (
    '/restapi/v1.0/account/2399766010/extension/2399766010/presence'
    '?detailedTelephonyState=true&sipData=true'
)


def _outbound_ringing_payload():
    return {
        'uuid': '9193027709140082382',
        'event': EVENT_PATH,
        'timestamp': '2026-06-11T07:35:23.600Z',
        'body': {
            'extensionId': 2399766010,
            'telephonyStatus': 'Ringing',
            'activeCalls': [{
                'id': 'r0f1drocu31rkrt3c9ta',
                'direction': 'Outbound',
                'from': '+17144927516',
                'to': '+17142426520',
                'telephonyStatus': 'Ringing',
                'sessionId': SESSION_ID,
                'startTime': '2026-06-11T07:35:23.532Z',
                'partyId': 'p-a786c452970f2z19eb59b7075z15521780000-1',
                'telephonySessionId': TELEPHONY_SESSION_ID,
            }],
            'sequence': 774310167,
            'aggregatedTelephonyStatus': 'Ringing',
        },
    }


def _outbound_connected_payload():
    return {
        'uuid': '5990681374080679326',
        'event': EVENT_PATH,
        'timestamp': '2026-06-11T07:35:24.320Z',
        'body': {
            'extensionId': 2399766010,
            'telephonyStatus': 'CallConnected',
            'activeCalls': [{
                'id': 'r0f1drocu31rkrt3c9ta',
                'direction': 'Outbound',
                'fromName': 'Vimesh Chaudhari',
                'from': '+17144927516',
                'toName': 'Vimesh Chaudhari',
                'to': '+17142426520',
                'telephonyStatus': 'CallConnected',
                'sessionId': SESSION_ID,
                'startTime': '2026-06-11T07:35:23.532Z',
                'partyId': 'p-a786c452970f2z19eb59b7075z15521780000-1',
                'telephonySessionId': TELEPHONY_SESSION_ID,
            }],
            'sequence': 774310168,
            'aggregatedTelephonyStatus': 'CallConnected',
        },
    }


def _internal_ringing_payload():
    return {
        'uuid': '3655547837530519764',
        'event': EVENT_PATH,
        'timestamp': '2026-06-11T07:35:29.257Z',
        'body': {
            'extensionId': 2399766010,
            'telephonyStatus': 'Ringing',
            'activeCalls': [{
                'id': 's-a786c452970f2z19eb59b7075z15521780000',
                'direction': 'Inbound',
                'from': '101',
                'to': '+17142426520',
                'telephonyStatus': 'Ringing',
                'sessionId': SESSION_ID,
                'startTime': '2026-06-11T07:35:29.188Z',
                'partyId': 'p-a786c452970f2z19eb59b7075z15521780000-2',
                'telephonySessionId': TELEPHONY_SESSION_ID,
            }],
            'sequence': 774310169,
            'aggregatedTelephonyStatus': 'Ringing',
        },
    }


def _internal_connected_payload():
    return {
        'uuid': '3821280100843832133',
        'event': EVENT_PATH,
        'timestamp': '2026-06-11T07:35:34.797Z',
        'body': {
            'extensionId': 2399766010,
            'telephonyStatus': 'CallConnected',
            'activeCalls': [{
                'id': '0a6df2ea-b67f-457a-9af7-2a3b7bd6e7a3',
                'direction': 'Inbound',
                'from': '101',
                'to': '+17142426520',
                'telephonyStatus': 'CallConnected',
                'sessionId': SESSION_ID,
                'startTime': '2026-06-11T07:35:29.188Z',
                'partyId': 'p-a786c452970f2z19eb59b7075z15521780000-2',
                'telephonySessionId': TELEPHONY_SESSION_ID,
            }],
            'sequence': 774310170,
            'aggregatedTelephonyStatus': 'CallConnected',
        },
    }


def _internal_ended_payload():
    return {
        'uuid': '2058141751460174759',
        'event': EVENT_PATH,
        'timestamp': '2026-06-11T07:35:48.906Z',
        'body': {
            'extensionId': 2399766010,
            'telephonyStatus': 'NoCall',
            'activeCalls': [{
                'id': '0a6df2ea-b67f-457a-9af7-2a3b7bd6e7a3',
                'direction': 'Inbound',
                'from': '101',
                'to': '+17142426520',
                'telephonyStatus': 'NoCall',
                'sessionId': SESSION_ID,
                'terminationType': 'final',
                'startTime': '2026-06-11T07:35:29.188Z',
                'partyId': 'p-a786c452970f2z19eb59b7075z15521780000-2',
                'telephonySessionId': TELEPHONY_SESSION_ID,
            }],
            'sequence': 774310171,
            'aggregatedTelephonyStatus': 'NoCall',
        },
    }


def _outbound_ended_payload():
    return {
        'uuid': '5059656288236515736',
        'event': EVENT_PATH,
        'timestamp': '2026-06-11T07:35:48.959Z',
        'body': {
            'extensionId': 2399766010,
            'telephonyStatus': 'NoCall',
            'activeCalls': [{
                'id': 'r0f1drocu31rkrt3c9ta',
                'direction': 'Outbound',
                'from': '+17144927516',
                'to': '+17142426520',
                'telephonyStatus': 'NoCall',
                'sessionId': SESSION_ID,
                'terminationType': 'final',
                'startTime': '2026-06-11T07:35:23.532Z',
                'partyId': 'p-a786c452970f2z19eb59b7075z15521780000-1',
                'telephonySessionId': TELEPHONY_SESSION_ID,
            }],
            'sequence': 774310172,
            'aggregatedTelephonyStatus': 'NoCall',
        },
    }


def _inbound_external_ringing_payload():
    return {
        'uuid': 'inbound-test-1',
        'event': EVENT_PATH,
        'timestamp': '2026-06-11T08:00:00.000Z',
        'body': {
            'telephonyStatus': 'Ringing',
            'activeCalls': [{
                'direction': 'Inbound',
                'from': '+15551234567',
                'to': '+17144927516',
                'telephonyStatus': 'Ringing',
                'sessionId': '999888777',
                'startTime': '2026-06-11T08:00:00.000Z',
            }],
            'sequence': 1,
            'aggregatedTelephonyStatus': 'Ringing',
        },
    }


class TestPresenceWebhookHelpers(unittest.TestCase):
    def test_extract_phone_string_and_dict(self):
        self.assertEqual(pw_utils.extract_phone('+17142426520'), '+17142426520')
        self.assertEqual(pw_utils.extract_phone({'phoneNumber': '+17142426520'}), '+17142426520')

    def test_is_internal_agent_leg(self):
        internal = {'direction': 'Inbound', 'from': '101'}
        external = {'direction': 'Inbound', 'from': '+15551234567'}
        outbound = {'direction': 'Outbound', 'from': '+17144927516'}
        self.assertTrue(pw_utils.is_internal_agent_leg(internal))
        self.assertFalse(pw_utils.is_internal_agent_leg(external))
        self.assertFalse(pw_utils.is_internal_agent_leg(outbound))

    def test_select_business_call_leg_prefers_inbound_external_caller(self):
        legs = [
            {'direction': 'Outbound', 'from': '+17144927516', 'to': '+17142426520'},
            {'direction': 'Inbound', 'from': '+15551234567', 'to': '+17144927516'},
        ]
        selected = pw_utils.select_business_call_leg(legs)
        self.assertEqual(selected['direction'], 'Inbound')
        self.assertEqual(pw_utils.extract_phone(selected.get('from')), '+15551234567')

    def test_select_business_call_leg_outbound_to_external(self):
        legs = [
            {'direction': 'Inbound', 'from': '101'},
            {'direction': 'Outbound', 'from': '+17144927516', 'to': '+17142426520'},
        ]
        selected = pw_utils.select_business_call_leg(legs)
        self.assertEqual(selected['direction'], 'Outbound')

    def test_map_presence_status(self):
        self.assertEqual(pw_utils.map_presence_status('Ringing'), 'ringing')
        self.assertEqual(pw_utils.map_presence_status('Proceeding'), 'ringing')
        self.assertEqual(pw_utils.map_presence_status('Setup'), 'ringing')
        self.assertEqual(pw_utils.map_presence_status('CallConnected'), 'answered')
        self.assertEqual(pw_utils.map_presence_status('NoCall'), 'no-answer')
        self.assertEqual(pw_utils.map_presence_status('NoCall', was_answered=True), 'completed')

    def test_collect_session_aliases_prefers_telephony_session_id(self):
        legs = [{
            'sessionId': SESSION_ID,
            'telephonySessionId': TELEPHONY_SESSION_ID,
        }]
        info = pw_utils.collect_session_aliases(legs, {})
        self.assertEqual(info['primary_key'], TELEPHONY_SESSION_ID)
        self.assertEqual(info['canonical_id'], SESSION_ID)
        self.assertEqual(info['telephony_session_id'], TELEPHONY_SESSION_ID)
        self.assertEqual(info['numeric_session_id'], SESSION_ID)
        self.assertIn(SESSION_ID, info['aliases'])
        self.assertIn(TELEPHONY_SESSION_ID, info['aliases'])

    def test_extract_caller_name_from_from_name(self):
        self.assertEqual(
            pw_utils.extract_caller_name({'fromName': 'Vimesh Chaudhari'}),
            'Vimesh Chaudhari',
        )


@tagged('post_install', '-at_install')
class TestPresenceWebhookProcessing(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.config = cls.env['ringcentral.config'].create({
            'name': 'Test RC Config',
            'client_id': 'test_client',
            'client_secret': 'test_secret',
        })
        cls.CallHistory = cls.env['ringcentral.call.history']

    def _process(self, payload):
        self.CallHistory.process_presence_webhook(self.config, payload)

    def _get_call(self):
        return self.CallHistory.search([
            ('ringcentral_call_id', '=', SESSION_ID),
            ('config_id', '=', self.config.id),
        ], limit=1)

    def test_outbound_call_lifecycle_preserves_direction(self):
        self.env['res.partner'].create({
            'name': 'Outbound Target',
            'phone': '+17142426520',
        })
        self._process(_outbound_ringing_payload())
        call = self._get_call()
        self.assertTrue(call)
        self.assertEqual(call.direction, 'outbound')
        self.assertEqual(call.from_number, '+17144927516')
        self.assertEqual(call.to_number, '+17142426520')
        self.assertEqual(call.status, 'ringing')

        self._process(_outbound_connected_payload())
        call = self._get_call()
        self.assertEqual(call.direction, 'outbound')
        self.assertEqual(call.from_number, '+17144927516')
        self.assertEqual(call.to_number, '+17142426520')
        self.assertEqual(call.status, 'answered')

        self._process(_internal_ringing_payload())
        call = self._get_call()
        self.assertEqual(call.direction, 'outbound')
        self.assertEqual(call.from_number, '+17144927516')
        self.assertEqual(call.to_number, '+17142426520')
        self.assertEqual(call.status, 'answered')

        self._process(_internal_connected_payload())
        call = self._get_call()
        self.assertEqual(call.direction, 'outbound')
        self.assertEqual(call.status, 'answered')

        self._process(_internal_ended_payload())
        call = self._get_call()
        self.assertEqual(call.direction, 'outbound')
        self.assertEqual(call.status, 'completed')
        self.assertTrue(call.end_time)
        self.assertGreater(call.duration, 0)

        self._process(_outbound_ended_payload())
        call = self._get_call()
        self.assertEqual(call.direction, 'outbound')
        self.assertEqual(call.from_number, '+17144927516')
        self.assertEqual(call.to_number, '+17142426520')
        self.assertEqual(call.status, 'completed')
        self.assertEqual(len(call.webhook_payloads), 6)

    def test_single_call_multi_leg_presence_webhooks_one_record(self):
        """Sandbox-style multi-leg webhooks for one session must yield a single call row."""
        self.env['res.partner'].create({
            'name': 'Outbound Target',
            'phone': '+17142426520',
        })
        payloads = [
            _outbound_ringing_payload(),
            _outbound_connected_payload(),
            _internal_ringing_payload(),
            _internal_connected_payload(),
            _internal_ended_payload(),
            _outbound_ended_payload(),
        ]
        for payload in payloads:
            self._process(payload)

        calls = self.CallHistory.search([
            ('config_id', '=', self.config.id),
            '|',
            ('ringcentral_call_id', '=', SESSION_ID),
            ('ringcentral_telephony_session_id', '=', TELEPHONY_SESSION_ID),
        ])
        self.assertEqual(len(calls), 1)
        call = calls[0]
        self.assertEqual(call.direction, 'outbound')
        self.assertEqual(call.from_number, '+17144927516')
        self.assertEqual(call.to_number, '+17142426520')
        self.assertEqual(call.status, 'completed')
        self.assertTrue(call.to_partner_id)

    def test_inbound_external_call_created(self):
        self.env['res.partner'].create({
            'name': 'Inbound Caller',
            'phone': '+15551234567',
        })
        self._process(_inbound_external_ringing_payload())
        call = self.CallHistory.search([
            ('ringcentral_call_id', '=', '999888777'),
        ], limit=1)
        self.assertTrue(call)
        self.assertEqual(call.direction, 'inbound')
        self.assertEqual(call.from_number, '+15551234567')
        self.assertEqual(call.status, 'ringing')
        self.assertEqual(call.from_partner_id.phone, '+15551234567')

    def test_inbound_partner_call_from_mobile(self):
        """Partner calling the business line should be inbound in Odoo."""
        self.env['res.partner'].create({
            'name': 'Mobile Caller',
            'phone': '+17142426520',
        })
        payload = {
            'uuid': 'inbound-mobile-1',
            'event': EVENT_PATH,
            'timestamp': '2026-06-11T10:00:00.000Z',
            'body': {
                'telephonyStatus': 'Ringing',
                'activeCalls': [{
                    'direction': 'Inbound',
                    'from': '+17142426520',
                    'to': '+17144927516',
                    'telephonyStatus': 'Ringing',
                    'sessionId': '111222333',
                    'startTime': '2026-06-11T10:00:00.000Z',
                }],
                'sequence': 1,
                'aggregatedTelephonyStatus': 'Ringing',
            },
        }
        self.CallHistory.process_presence_webhook(self.config, payload)
        call = self.CallHistory.search([('ringcentral_call_id', '=', '111222333')], limit=1)
        self.assertTrue(call)
        self.assertEqual(call.direction, 'inbound')
        self.assertEqual(call.from_number, '+17142426520')
        self.assertEqual(call.to_partner_id.id, False)
        self.assertEqual(call.from_partner_id.phone, '+17142426520')

    def test_inbound_links_from_partner_by_caller_phone(self):
        """Inbound call links from_partner_id when caller matches contact mobile."""
        self.env['res.partner'].create({
            'name': 'Mobile Inbound Caller',
            'mobile': '+15559876543',
        })
        payload = {
            'uuid': 'inbound-mobile-link-1',
            'event': EVENT_PATH,
            'timestamp': '2026-06-11T10:30:00.000Z',
            'body': {
                'telephonyStatus': 'Ringing',
                'activeCalls': [{
                    'direction': 'Inbound',
                    'from': '+15559876543',
                    'to': '+17144927516',
                    'telephonyStatus': 'Ringing',
                    'sessionId': 'mobile-link-session',
                    'startTime': '2026-06-11T10:30:00.000Z',
                }],
                'sequence': 1,
                'aggregatedTelephonyStatus': 'Ringing',
            },
        }
        self.CallHistory.process_presence_webhook(self.config, payload)
        call = self.CallHistory.search([('ringcentral_call_id', '=', 'mobile-link-session')], limit=1)
        self.assertTrue(call)
        self.assertEqual(call.direction, 'inbound')
        self.assertTrue(call.from_partner_id)
        self.assertEqual(call.from_partner_id.mobile, '+15559876543')
        self.assertFalse(call.to_partner_id)

    def test_inbound_external_caller_when_company_line_is_contact(self):
        """Inbound mobile call stays inbound when the business line is stored as a contact."""
        self.env['res.partner'].create({
            'name': 'Company Line',
            'phone': '+17144927516',
        })
        self.env['res.partner'].create({
            'name': 'Mobile Caller',
            'mobile': '+17142426520',
        })
        payload = {
            'uuid': 'inbound-company-line-contact',
            'event': EVENT_PATH,
            'timestamp': '2026-06-11T11:00:00.000Z',
            'body': {
                'telephonyStatus': 'Ringing',
                'activeCalls': [{
                    'direction': 'Inbound',
                    'from': '+17142426520',
                    'to': '+17144927516',
                    'telephonyStatus': 'Ringing',
                    'sessionId': 'company-line-inbound',
                    'startTime': '2026-06-11T11:00:00.000Z',
                }],
                'sequence': 1,
                'aggregatedTelephonyStatus': 'Ringing',
            },
        }
        self.CallHistory.process_presence_webhook(self.config, payload)
        call = self.CallHistory.search([('ringcentral_call_id', '=', 'company-line-inbound')], limit=1)
        self.assertTrue(call)
        self.assertEqual(call.direction, 'inbound')
        self.assertEqual(call.from_number, '+17142426520')
        self.assertEqual(call.to_number, '+17144927516')
        self.assertTrue(call.from_partner_id)
        self.assertEqual(call.from_partner_id.mobile, '+17142426520')

    def test_inbound_links_partner_with_digits_only_phone(self):
        """Caller number without country code should still match stored contact phone."""
        self.env['res.partner'].create({
            'name': 'Digits Caller',
            'phone': '7142426520',
        })
        payload = {
            'uuid': 'inbound-digits-only',
            'event': EVENT_PATH,
            'timestamp': '2026-06-11T11:15:00.000Z',
            'body': {
                'telephonyStatus': 'Ringing',
                'activeCalls': [{
                    'direction': 'Inbound',
                    'from': '+17142426520',
                    'to': '+17144927516',
                    'telephonyStatus': 'Ringing',
                    'sessionId': 'digits-only-inbound',
                    'startTime': '2026-06-11T11:15:00.000Z',
                }],
                'sequence': 1,
                'aggregatedTelephonyStatus': 'Ringing',
            },
        }
        self.CallHistory.process_presence_webhook(self.config, payload)
        call = self.CallHistory.search([('ringcentral_call_id', '=', 'digits-only-inbound')], limit=1)
        self.assertTrue(call)
        self.assertEqual(call.direction, 'inbound')
        self.assertTrue(call.from_partner_id)
        self.assertEqual(call.from_partner_id.name, 'Digits Caller')

    def test_inbound_links_partner_with_formatted_contact_phone(self):
        """Webhook E.164 number must match formatted CRM phone like +1 714-242-6520."""
        self.env['res.partner'].create({
            'name': 'Formatted Caller',
            'phone': '+1 714-242-6520',
        })
        payload = {
            'uuid': 'inbound-formatted-phone',
            'event': EVENT_PATH,
            'timestamp': '2026-06-11T11:30:00.000Z',
            'body': {
                'telephonyStatus': 'Ringing',
                'activeCalls': [{
                    'direction': 'Inbound',
                    'from': '+17142426520',
                    'to': '+17144927516',
                    'telephonyStatus': 'Ringing',
                    'sessionId': 'formatted-inbound-session',
                    'startTime': '2026-06-11T11:30:00.000Z',
                }],
                'sequence': 1,
                'aggregatedTelephonyStatus': 'Ringing',
            },
        }
        self.CallHistory.process_presence_webhook(self.config, payload)
        call = self.CallHistory.search([('ringcentral_call_id', '=', 'formatted-inbound-session')], limit=1)
        self.assertTrue(call)
        self.assertEqual(call.direction, 'inbound')
        self.assertTrue(call.from_partner_id)
        self.assertEqual(call.from_partner_id.name, 'Formatted Caller')

    def test_outbound_links_partner_with_formatted_contact_phone(self):
        """Outbound callee with formatted CRM phone must link to_partner_id."""
        self.env['res.partner'].create({
            'name': 'Formatted Callee',
            'phone': '+1 714-242-6520',
        })
        self._process(_outbound_ringing_payload())
        call = self._get_call()
        self.assertEqual(call.direction, 'outbound')
        self.assertTrue(call.to_partner_id)
        self.assertEqual(call.to_partner_id.name, 'Formatted Callee')

    def test_outbound_links_to_partner_by_callee_phone(self):
        """Outbound call links to_partner_id when callee matches a contact."""
        self.env['res.partner'].create({
            'name': 'Outbound Callee',
            'phone': '+17142426520',
        })
        self._process(_outbound_ringing_payload())
        call = self._get_call()
        self.assertEqual(call.direction, 'outbound')
        self.assertTrue(call.to_partner_id)
        self.assertEqual(call.to_partner_id.phone, '+17142426520')
        self.assertFalse(call.from_partner_id)

    def test_sync_create_infers_inbound_from_partner_caller(self):
        self.env['res.partner'].create({
            'name': 'Caller Contact',
            'phone': '+17142426520',
        })
        log_record = {
            'id': 'inboundlog1',
            'sessionId': '444555666',
            'startTime': '2026-06-11T10:00:00.000Z',
            'duration': 30,
            'direction': 'Outbound',
            'result': 'Accepted',
            'from': {'phoneNumber': '+17142426520'},
            'to': {'phoneNumber': '+17144927516'},
        }
        action, call = self.CallHistory.sync_from_call_log_record(self.config, log_record)
        self.assertEqual(action, 'created')
        self.assertEqual(call.direction, 'inbound')

    def test_internal_only_webhook_does_not_create_record(self):
        before = self.CallHistory.search_count([])
        self._process(_internal_ringing_payload())
        self.assertEqual(self.CallHistory.search_count([]), before)

    def test_missed_call_shows_no_answer_not_completed(self):
        self.env['res.partner'].create({
            'name': 'Missed Caller',
            'phone': '+17142426520',
        })
        self._process(_outbound_ringing_payload())
        call = self._get_call()
        self.assertEqual(call.status, 'ringing')

        missed_end = {
            'uuid': 'missed-end-1',
            'event': EVENT_PATH,
            'timestamp': '2026-06-11T07:36:00.000Z',
            'body': {
                'telephonyStatus': 'NoCall',
                'activeCalls': [{
                    'id': 'r0f1drocu31rkrt3c9ta',
                    'direction': 'Outbound',
                    'from': '+17144927516',
                    'to': '+17142426520',
                    'telephonyStatus': 'NoCall',
                    'sessionId': SESSION_ID,
                    'terminationType': 'final',
                    'startTime': '2026-06-11T07:35:23.532Z',
                    'partyId': 'p-a786c452970f2z19eb59b7075z15521780000-1',
                    'telephonySessionId': TELEPHONY_SESSION_ID,
                }],
                'sequence': 774310200,
                'aggregatedTelephonyStatus': 'NoCall',
            },
        }
        self._process(missed_end)
        call = self._get_call()
        self.assertEqual(call.status, 'no-answer')
        self.assertEqual(call.direction, 'outbound')

    def test_sync_updates_webhook_record_by_session_id(self):
        self.env['res.partner'].create({
            'name': 'Call Target',
            'phone': '+17142426520',
        })
        self._process(_outbound_ringing_payload())
        self._process(_outbound_connected_payload())
        call = self._get_call()
        self.assertEqual(call.direction, 'outbound')

        log_record = {
            'id': 'IXPCm_tIkCduk4I',
            'sessionId': SESSION_ID,
            'startTime': '2026-06-11T07:35:23.532Z',
            'duration': 25,
            'direction': 'Inbound',
            'result': 'Accepted',
            'from': {'phoneNumber': '101'},
            'to': {'phoneNumber': '+17142426520'},
            'recording': {'id': '401547458008'},
        }
        action, synced = self.CallHistory.sync_from_call_log_record(self.config, log_record)
        self.assertEqual(action, 'updated')
        self.assertEqual(synced.id, call.id)
        self.assertEqual(synced.direction, 'outbound')
        self.assertEqual(synced.from_number, '+17144927516')
        self.assertEqual(synced.to_number, '+17142426520')
        self.assertEqual(synced.recording_id, '401547458008')
        self.assertEqual(synced.ringcentral_call_log_id, 'IXPCm_tIkCduk4I')

    def test_sync_creates_when_no_webhook_record(self):
        log_record = {
            'id': 'newlog123',
            'sessionId': '555444333',
            'startTime': '2026-06-11T09:00:00.000Z',
            'duration': 60,
            'direction': 'Outbound',
            'result': 'Accepted',
            'from': {'phoneNumber': '+17144927516'},
            'to': {'phoneNumber': '+17142426520'},
            'recording': {'id': 'rec999'},
        }
        action, call = self.CallHistory.sync_from_call_log_record(self.config, log_record)
        self.assertEqual(action, 'created')
        self.assertEqual(call.ringcentral_call_id, '555444333')
        self.assertEqual(call.direction, 'outbound')
        self.assertEqual(call.recording_id, 'rec999')

    def test_internal_connected_sets_answered_by_extension(self):
        agent = self.env['res.users'].create({
            'name': 'RC Agent 101',
            'login': 'rc_agent_101@test.com',
            'ringcentral_extension': '101',
            'ringcentral_extension_id': '2399766010',
        })
        self.env['res.partner'].create({
            'name': 'Outbound Target',
            'phone': '+17142426520',
        })
        self._process(_outbound_ringing_payload())
        self._process(_internal_connected_payload())
        call = self._get_call()
        self.assertEqual(call.answered_by_id, agent)
        self.assertEqual(call.user_id, agent)

    def test_security_user_sees_initiated_or_answered_calls(self):
        initiator = self.env['res.users'].create({
            'name': 'Outbound Initiator',
            'login': 'rc_initiator@test.com',
            'group_ids': [(4, self.env.ref('ringcentral_integration.group_ringcentral_user').id)],
        })
        answerer = self.env['res.users'].create({
            'name': 'Inbound Answerer',
            'login': 'rc_answerer@test.com',
            'group_ids': [(4, self.env.ref('ringcentral_integration.group_ringcentral_user').id)],
        })
        outbound = self.CallHistory.create({
            'config_id': self.config.id,
            'direction': 'outbound',
            'from_number': '+17144927516',
            'to_number': '+17142426520',
            'start_time': fields.Datetime.now(),
            'status': 'completed',
            'initiated_by_id': initiator.id,
            'ringcentral_call_id': 'security-outbound-1',
        })
        inbound = self.CallHistory.create({
            'config_id': self.config.id,
            'direction': 'inbound',
            'from_number': '+15551234567',
            'to_number': '+17144927516',
            'start_time': fields.Datetime.now(),
            'status': 'completed',
            'answered_by_id': answerer.id,
            'ringcentral_call_id': 'security-inbound-1',
        })
        initiator_calls = self.CallHistory.with_user(initiator).search([
            ('id', 'in', [outbound.id, inbound.id]),
        ])
        self.assertIn(outbound, initiator_calls)
        self.assertNotIn(inbound, initiator_calls)
        answerer_calls = self.CallHistory.with_user(answerer).search([
            ('id', 'in', [outbound.id, inbound.id]),
        ])
        self.assertIn(inbound, answerer_calls)
        self.assertNotIn(outbound, answerer_calls)

    def test_full_outbound_lifecycle_user_payloads(self):
        agent = self.env['res.users'].create({
            'name': 'RC Agent 101',
            'login': 'rc_agent_full@test.com',
            'ringcentral_extension': '101',
            'ringcentral_extension_id': '2399766010',
        })
        self.env['res.partner'].create({
            'name': 'Outbound Target',
            'phone': '+17142426520',
        })
        payloads = [
            _outbound_ringing_payload(),
            _outbound_connected_payload(),
            _internal_ringing_payload(),
            _internal_connected_payload(),
            _internal_ended_payload(),
            _outbound_ended_payload(),
        ]
        for payload in payloads:
            payload['ownerId'] = '2399766010'
            self._process(payload)

        calls = self.CallHistory.search([('config_id', '=', self.config.id)])
        self.assertEqual(len(calls), 1)
        call = calls[0]
        self.assertEqual(call.direction, 'outbound')
        self.assertEqual(call.from_number, '+17144927516')
        self.assertEqual(call.to_number, '+17142426520')
        self.assertEqual(call.ringcentral_call_id, SESSION_ID)
        self.assertEqual(call.ringcentral_telephony_session_id, TELEPHONY_SESSION_ID)
        self.assertEqual(call.to_partner_id.phone, '+17142426520')
        self.assertEqual(call.initiated_by_id, agent)
        self.assertEqual(call.answered_by_id, agent)
        self.assertEqual(call.caller_name, 'Vimesh Chaudhari')
        self.assertEqual(call.status, 'completed')
        self.assertEqual(len(call.webhook_payloads), 6)

    def test_direction_when_both_numbers_are_contacts(self):
        self.env['res.partner'].create({
            'name': 'Company Line',
            'phone': '+17144927516',
        })
        self.env['res.partner'].create({
            'name': 'Outbound Target',
            'phone': '+17142426520',
        })
        self._process(_outbound_ringing_payload())
        call = self._get_call()
        self.assertEqual(call.direction, 'outbound')

    def test_direction_from_contact_is_inbound(self):
        """Contact on from_number is treated as inbound."""
        self.env['res.partner'].create({
            'name': 'Known Caller',
            'phone': '+15551234567',
        })
        self._process(_inbound_external_ringing_payload())
        call = self.CallHistory.search([('ringcentral_call_id', '=', '999888777')], limit=1)
        self.assertEqual(call.direction, 'inbound')
        self.assertTrue(call.from_partner_id)
        self.assertEqual(call.from_partner_id.phone, '+15551234567')

    def test_direction_to_contact_is_outbound(self):
        """Contact on to_number is treated as outbound."""
        self.env['res.partner'].create({
            'name': 'Outbound Target',
            'phone': '+17142426520',
        })
        self._process(_outbound_ringing_payload())
        call = self._get_call()
        self.assertEqual(call.direction, 'outbound')
        self.assertTrue(call.to_partner_id)

    def test_direction_unknown_caller_uses_rc_leg(self):
        """When neither leg matches a contact, use RingCentral direction."""
        self._process(_inbound_external_ringing_payload())
        call = self.CallHistory.search([('ringcentral_call_id', '=', '999888777')], limit=1)
        self.assertTrue(call)
        self.assertEqual(call.direction, 'inbound')
        self.assertFalse(call.from_partner_id)

    def test_session_id_alias_dedup(self):
        alias_payload = {
            'uuid': 'alias-create-1',
            'event': EVENT_PATH,
            'timestamp': '2026-06-11T07:35:23.600Z',
            'ownerId': '2399766010',
            'body': {
                'extensionId': 2399766010,
                'telephonyStatus': 'Ringing',
                'activeCalls': [{
                    'direction': 'Outbound',
                    'from': '+17144927516',
                    'to': '+17142426520',
                    'telephonyStatus': 'Ringing',
                    'telephonySessionId': TELEPHONY_SESSION_ID,
                    'startTime': '2026-06-11T07:35:23.532Z',
                }],
                'sequence': 1,
                'aggregatedTelephonyStatus': 'Ringing',
            },
        }
        self._process(alias_payload)
        self._process(_outbound_ringing_payload())
        calls = self.CallHistory.search([('config_id', '=', self.config.id)])
        self.assertEqual(len(calls), 1)
        call = calls[0]
        self.assertEqual(call.ringcentral_call_id, SESSION_ID)
        self.assertEqual(call.ringcentral_telephony_session_id, TELEPHONY_SESSION_ID)

    def test_presence_and_telephony_same_session_one_record(self):
        self.env['res.partner'].create({
            'name': 'Outbound Target',
            'phone': '+17142426520',
        })
        self._process(_outbound_ringing_payload())
        self.CallHistory.process_telephony_session_webhook(
            self.config, _telephony_outbound_same_session_payload(),
        )
        calls = self.CallHistory.search([
            ('config_id', '=', self.config.id),
            '|',
            ('ringcentral_call_id', '=', SESSION_ID),
            ('ringcentral_telephony_session_id', '=', TELEPHONY_SESSION_ID),
        ])
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls.direction, 'outbound')


def _telephony_outbound_same_session_payload():
    return {
        'uuid': 'telephony-outbound-same-session',
        'event': '/restapi/v1.0/account/2399766010/telephony/sessions',
        'timestamp': '2026-06-11T07:35:24.320Z',
        'body': {
            'sequence': 774310168,
            'sessionId': SESSION_ID,
            'telephonySessionId': TELEPHONY_SESSION_ID,
            'eventTime': '2026-06-11T07:35:24.320Z',
            'extensionId': 2399766010,
            'parties': [{
                'id': 'party-outbound-1',
                'direction': 'Outbound',
                'extensionId': 2399766010,
                'from': {'phoneNumber': '+17144927516', 'name': 'Vimesh Chaudhari'},
                'to': {'phoneNumber': '+17142426520', 'name': 'Vimesh Chaudhari'},
                'status': {'code': 'Answered'},
            }],
        },
    }


def _telephony_session_inbound_payload():
    return {
        'uuid': 'telephony-inbound-1',
        'event': '/restapi/v1.0/account/2399766010/telephony/sessions',
        'timestamp': '2026-06-16T10:00:00.000Z',
        'body': {
            'sequence': 1,
            'sessionId': '888777666',
            'telephonySessionId': 's-test-inbound',
            'eventTime': '2026-06-16T10:00:00.000Z',
            'extensionId': 2399766010,
            'parties': [{
                'id': 'party-1',
                'direction': 'Inbound',
                'extensionId': 2399766010,
                'from': {'phoneNumber': '+15551234567', 'name': 'Caller'},
                'to': {'phoneNumber': '+17144927516', 'name': 'Main Line'},
                'status': {'code': 'Proceeding'},
            }],
        },
    }


def _telephony_session_voicemail_payload():
    return {
        'uuid': 'telephony-voicemail-1',
        'event': '/restapi/v1.0/account/2399766010/telephony/sessions',
        'timestamp': '2026-06-16T10:05:00.000Z',
        'body': {
            'sequence': 2,
            'sessionId': '888777667',
            'telephonySessionId': 's-test-voicemail',
            'eventTime': '2026-06-16T10:05:00.000Z',
            'extensionId': 2399766010,
            'parties': [{
                'id': 'party-vm-1',
                'direction': 'Inbound',
                'extensionId': 2399766010,
                'from': {'phoneNumber': '17145550177', 'name': 'Caller Without Plus'},
                'to': {'phoneNumber': '+17144927516', 'name': 'Main Line'},
                'status': {'code': 'Voicemail'},
            }],
        },
    }


def _telephony_lifecycle_payloads():
    return [
        {
            'uuid': 'telephony-life-1',
            'event': '/restapi/v1.0/account/2399766010/telephony/sessions',
            'timestamp': '2026-06-17T08:00:00.000Z',
            'body': {
                'sequence': 1,
                'telephonySessionId': TELEPHONY_SESSION_ID,
                'eventTime': '2026-06-17T08:00:00.000Z',
                'extensionId': 2399766010,
                'parties': [{
                    'id': 'party-life-1',
                    'direction': 'Outbound',
                    'extensionId': 2399766010,
                    'from': {'phoneNumber': '+17144927516'},
                    'to': {'phoneNumber': '+17142426520'},
                    'status': {'code': 'Proceeding'},
                }],
            },
        },
        {
            'uuid': 'telephony-life-2',
            'event': '/restapi/v1.0/account/2399766010/telephony/sessions',
            'timestamp': '2026-06-17T08:00:05.000Z',
            'body': {
                'sequence': 2,
                'sessionId': SESSION_ID,
                'telephonySessionId': TELEPHONY_SESSION_ID,
                'eventTime': '2026-06-17T08:00:05.000Z',
                'extensionId': 2399766010,
                'parties': [{
                    'id': 'party-life-1',
                    'direction': 'Outbound',
                    'extensionId': 2399766010,
                    'from': {'phoneNumber': '+17144927516'},
                    'to': {'phoneNumber': '+17142426520'},
                    'status': {'code': 'Answered'},
                }],
            },
        },
        {
            'uuid': 'telephony-life-3',
            'event': '/restapi/v1.0/account/2399766010/telephony/sessions',
            'timestamp': '2026-06-17T08:01:00.000Z',
            'body': {
                'sequence': 3,
                'sessionId': SESSION_ID,
                'telephonySessionId': TELEPHONY_SESSION_ID,
                'eventTime': '2026-06-17T08:01:00.000Z',
                'extensionId': 2399766010,
                'parties': [{
                    'id': 'party-life-1',
                    'direction': 'Outbound',
                    'extensionId': 2399766010,
                    'from': {'phoneNumber': '+17144927516'},
                    'to': {'phoneNumber': '+17142426520'},
                    'status': {'code': 'Disconnected'},
                }],
            },
        },
    ]


@tagged('post_install', '-at_install')
class TestTelephonySessionWebhook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.config = cls.env['ringcentral.config'].create({
            'name': 'Telephony Test Config',
            'client_id': 'telephony_client',
            'client_secret': 'telephony_secret',
        })
        cls.CallHistory = cls.env['ringcentral.call.history']

    def test_telephony_session_webhook_creates_inbound_call(self):
        self.env['res.partner'].create({
            'name': 'Telephony Caller',
            'phone': '+15551234567',
        })
        self.CallHistory.process_telephony_session_webhook(
            self.config, _telephony_session_inbound_payload(),
        )
        call = self.CallHistory.search([
            ('ringcentral_call_id', '=', '888777666'),
            ('config_id', '=', self.config.id),
        ], limit=1)
        self.assertTrue(call)
        self.assertEqual(call.direction, 'inbound')
        self.assertEqual(call.from_number, '+15551234567')
        self.assertEqual(call.status, 'ringing')

    def test_telephony_session_voicemail_sets_missed_result(self):
        self.env['res.partner'].create({
            'name': 'Caller Without Plus',
            'phone': '+17145550177',
        })
        self.CallHistory.process_telephony_session_webhook(
            self.config, _telephony_session_voicemail_payload(),
        )
        call = self.CallHistory.search([
            ('ringcentral_call_id', '=', '888777667'),
            ('config_id', '=', self.config.id),
        ], limit=1)
        self.assertTrue(call)
        self.assertEqual(call.direction, 'inbound')
        self.assertEqual(call.from_number, '17145550177')
        self.assertEqual(call.status, 'no-answer')
        self.assertEqual(call.call_result, 'missed')

    def test_telephony_lifecycle_single_record(self):
        self.env['res.partner'].create({
            'name': 'Lifecycle Target',
            'phone': '+17142426520',
        })
        for payload in _telephony_lifecycle_payloads():
            self.CallHistory.process_telephony_session_webhook(self.config, payload)
        calls = self.CallHistory.search([
            ('config_id', '=', self.config.id),
            '|',
            ('ringcentral_call_id', '=', SESSION_ID),
            ('ringcentral_telephony_session_id', '=', TELEPHONY_SESSION_ID),
        ])
        self.assertEqual(len(calls), 1)
        call = calls[0]
        self.assertEqual(call.ringcentral_call_id, SESSION_ID)
        self.assertEqual(call.ringcentral_telephony_session_id, TELEPHONY_SESSION_ID)
        self.assertEqual(call.direction, 'outbound')
        self.assertEqual(call.status, 'completed')

    def test_telephony_session_id_only_then_numeric_single_record(self):
        self.env['res.partner'].create({
            'name': 'Alias Target',
            'phone': '+17142426520',
        })
        self.CallHistory.process_telephony_session_webhook(
            self.config, _telephony_lifecycle_payloads()[0],
        )
        self.CallHistory.process_telephony_session_webhook(
            self.config, _telephony_lifecycle_payloads()[1],
        )
        calls = self.CallHistory.search([('config_id', '=', self.config.id)])
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls.ringcentral_telephony_session_id, TELEPHONY_SESSION_ID)
        self.assertEqual(calls.ringcentral_call_id, SESSION_ID)

    def test_separate_inbound_outbound_leg_events_one_record(self):
        self.env['res.partner'].create({
            'name': 'Sandbox Target',
            'phone': '+17142426520',
        })
        self.CallHistory.with_user(self.env['res.users'].create({
            'name': 'Dialer User',
            'login': 'rc_dialer@test.com',
            'group_ids': [(4, self.env.ref('ringcentral_integration.group_ringcentral_user').id)],
        })).process_call_event(
            'outbound_start',
            phone_number='+17142426520',
        )
        self.CallHistory.process_presence_webhook(self.config, _outbound_ringing_payload())
        inbound_leg = {
            **_inbound_external_ringing_payload(),
            'body': {
                **_inbound_external_ringing_payload()['body'],
                'activeCalls': [{
                    'direction': 'Inbound',
                    'from': '+15559998888',
                    'to': '+17144927516',
                    'telephonyStatus': 'Ringing',
                    'sessionId': SESSION_ID,
                    'telephonySessionId': TELEPHONY_SESSION_ID,
                    'startTime': '2026-06-11T08:00:00.000Z',
                }],
            },
        }
        self.CallHistory.process_presence_webhook(self.config, inbound_leg)
        calls = self.CallHistory.search([
            ('config_id', '=', self.config.id),
            '|',
            ('ringcentral_call_id', '=', SESSION_ID),
            ('ringcentral_telephony_session_id', '=', TELEPHONY_SESSION_ID),
        ])
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls.direction, 'outbound')

    def test_contact_normalization_links_partner(self):
        self.env['res.partner'].create({
            'name': 'Normalized Caller',
            'phone': '7142426520',
        })
        payload = {
            'uuid': 'normalized-contact-1',
            'event': EVENT_PATH,
            'timestamp': '2026-06-17T09:00:00.000Z',
            'body': {
                'telephonyStatus': 'Ringing',
                'sessionId': 'norm-session-1',
                'telephonySessionId': 's-norm-session-1',
                'activeCalls': [{
                    'direction': 'Inbound',
                    'from': '+17142426520',
                    'to': '+17144927516',
                    'telephonyStatus': 'Ringing',
                    'sessionId': 'norm-session-1',
                    'telephonySessionId': 's-norm-session-1',
                    'startTime': '2026-06-17T09:00:00.000Z',
                }],
                'sequence': 1,
                'aggregatedTelephonyStatus': 'Ringing',
            },
        }
        self.CallHistory.process_presence_webhook(self.config, payload)
        call = self.CallHistory.search([
            ('ringcentral_telephony_session_id', '=', 's-norm-session-1'),
        ], limit=1)
        self.assertTrue(call)
        self.assertTrue(call.from_partner_id)
        self.assertEqual(call.from_partner_id.phone, '7142426520')

    def test_two_inbound_calls_same_number_create_separate_records(self):
        """Two inbound calls from the same number must create distinct history rows."""
        caller = '+15551234567'
        self.env['res.partner'].create({'name': 'Repeat Caller', 'phone': caller})
        for session_id in ('inbound-session-a', 'inbound-session-b'):
            self._process({
                'uuid': f'two-call-{session_id}',
                'event': EVENT_PATH,
                'timestamp': '2026-06-17T10:00:00.000Z',
                'body': {
                    'telephonyStatus': 'Ringing',
                    'activeCalls': [{
                        'direction': 'Inbound',
                        'from': caller,
                        'to': '+17144927516',
                        'telephonyStatus': 'Ringing',
                        'sessionId': session_id,
                        'startTime': '2026-06-17T10:00:00.000Z',
                    }],
                    'sequence': 1,
                    'aggregatedTelephonyStatus': 'Ringing',
                },
            })
        calls = self.CallHistory.search([
            ('config_id', '=', self.config.id),
            ('from_number', '=', caller),
        ])
        self.assertEqual(len(calls), 2)
        self.assertEqual(
            set(calls.mapped('ringcentral_call_id')),
            {'inbound-session-a', 'inbound-session-b'},
        )

    def test_second_inbound_does_not_merge_completed_call(self):
        """A new inbound session must not update a completed call from the same number."""
        caller = '+15559876543'
        self._process({
            'uuid': 'completed-call-a',
            'event': EVENT_PATH,
            'timestamp': '2026-06-17T11:00:00.000Z',
            'body': {
                'telephonyStatus': 'NoCall',
                'activeCalls': [{
                    'direction': 'Inbound',
                    'from': caller,
                    'to': '+17144927516',
                    'telephonyStatus': 'NoCall',
                    'sessionId': 'completed-session-a',
                    'startTime': '2026-06-17T10:59:00.000Z',
                    'terminationType': 'final',
                }],
                'sequence': 1,
                'aggregatedTelephonyStatus': 'NoCall',
            },
        })
        call_a = self.CallHistory.search([
            ('ringcentral_call_id', '=', 'completed-session-a'),
        ], limit=1)
        self.assertTrue(call_a)
        self.assertEqual(call_a.status, 'no-answer')

        self._process({
            'uuid': 'new-call-b',
            'event': EVENT_PATH,
            'timestamp': '2026-06-17T11:05:00.000Z',
            'body': {
                'telephonyStatus': 'Ringing',
                'activeCalls': [{
                    'direction': 'Inbound',
                    'from': caller,
                    'to': '+17144927516',
                    'telephonyStatus': 'Ringing',
                    'sessionId': 'new-session-b',
                    'startTime': '2026-06-17T11:05:00.000Z',
                }],
                'sequence': 1,
                'aggregatedTelephonyStatus': 'Ringing',
            },
        })
        call_b = self.CallHistory.search([
            ('ringcentral_call_id', '=', 'new-session-b'),
        ], limit=1)
        self.assertTrue(call_b)
        self.assertNotEqual(call_b.id, call_a.id)
        call_a.invalidate_recordset()
        self.assertEqual(call_a.ringcentral_call_id, 'completed-session-a')
        self.assertEqual(call_a.status, 'no-answer')
