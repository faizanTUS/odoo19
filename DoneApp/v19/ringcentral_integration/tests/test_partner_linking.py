# -*- coding: utf-8 -*-
import unittest

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.ringcentral_integration.utils import phone as phone_utils


class TestPhoneMatchHelpers(unittest.TestCase):
    def test_phones_match_e164_and_local(self):
        self.assertTrue(phone_utils.phones_match('+17142426520', '7142426520'))
        self.assertTrue(phone_utils.phones_match('7142426520', '+1 (714) 242-6520'))

    def test_phones_match_last_ten_digits(self):
        self.assertTrue(phone_utils.phones_match('+17142426520', '7142426520'))

    def test_phones_match_rejects_different_numbers(self):
        self.assertFalse(phone_utils.phones_match('+17142426520', '+17142426521'))


@tagged('post_install', '-at_install')
class TestPartnerLinking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.config = cls.env['ringcentral.config'].create({
            'name': 'Partner Link Test Config',
            'client_id': 'partner_link_client',
            'client_secret': 'partner_link_secret',
        })
        cls.CallHistory = cls.env['ringcentral.call.history']

    def test_link_contact_from_phone_sets_from_partner(self):
        partner = self.env['res.partner'].create({
            'name': 'Link Helper Caller',
            'phone': '+17145550333',
        })
        call = self.CallHistory.create({
            'config_id': self.config.id,
            'direction': 'inbound',
            'from_number': '7145550333',
            'to_number': 'unknown',
            'status': 'ringing',
            'start_time': '2026-06-11T12:00:00',
        })
        linked = self.CallHistory.link_contact_from_phone('+17145550333')
        self.assertEqual(linked.id, call.id)
        self.assertEqual(call.from_partner_id, partner)
