# -*- coding: utf-8 -*-
import unittest

from odoo.addons.ringcentral_integration.utils import phone as phone_utils


class TestPhoneUtils(unittest.TestCase):
    def test_normalize_phone_strips_formatting(self):
        self.assertEqual(phone_utils.normalize_phone('+1 714-242-6520'), '17142426520')
        self.assertEqual(phone_utils.normalize_phone('+17142426520'), '17142426520')

    def test_phones_match_formatted_vs_e164(self):
        self.assertTrue(phone_utils.phones_match('+1 714-242-6520', '+17142426520'))
        self.assertTrue(phone_utils.phones_match('7142426520', '+17142426520'))

    def test_ilike_patterns_include_formatted_us_number(self):
        patterns = phone_utils.get_phone_ilike_patterns('+17142426520')
        self.assertIn('+1 714-242-6520', patterns)
        self.assertIn('714-242-6520', patterns)
