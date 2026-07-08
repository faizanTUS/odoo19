# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestRingCentralOAuth(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.config = cls.env['ringcentral.config'].create({
            'name': 'OAuth Test Config',
            'client_id': 'oauth_client',
            'client_secret': 'oauth_secret',
        })

    def test_oauth_state_roundtrip(self):
        payload = {
            'config_id': self.config.id,
            'return_url': '/web#action=123',
            'csrf': 'test-token',
        }
        encoded = self.env['ringcentral.config']._encode_oauth_state(payload)
        decoded = self.env['ringcentral.config']._decode_oauth_state(encoded)
        self.assertEqual(decoded['config_id'], self.config.id)
        self.assertEqual(decoded['return_url'], '/web#action=123')
        self.assertEqual(decoded['csrf'], 'test-token')

    def test_oauth_success_redirect(self):
        url = self.env['ringcentral.config']._build_oauth_success_redirect('/web')
        self.assertIn('ringcentral_status=success', url)

    def test_oauth_error_redirect(self):
        url = self.env['ringcentral.config']._build_oauth_error_redirect('/web', 'Token failed')
        self.assertIn('ringcentral_status=error', url)
        self.assertIn('ringcentral_message=', url)
