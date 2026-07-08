# -*- coding: utf-8 -*-

from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestRingCentralSecurity(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.config = cls.env['ringcentral.config'].create({
            'name': 'Security Test Config',
            'client_id': 'sec_client',
            'client_secret': 'sec_secret',
        })
        cls.admin_user = cls.env.ref('base.user_admin')
        cls.admin_user.write({
            'group_ids': [(4, cls.env.ref('ringcentral_integration.group_ringcentral_admin').id)],
        })
        cls.rc_user = cls.env['res.users'].create({
            'name': 'RC Security User',
            'login': 'rc_security_user@test.com',
            'group_ids': [(4, cls.env.ref('ringcentral_integration.group_ringcentral_user').id)],
        })
        cls.other_user = cls.env['res.users'].create({
            'name': 'RC Other User',
            'login': 'rc_other_user@test.com',
            'group_ids': [(4, cls.env.ref('ringcentral_integration.group_ringcentral_user').id)],
        })
        cls.own_call = cls.env['ringcentral.call.history'].create({
            'config_id': cls.config.id,
            'direction': 'inbound',
            'from_number': '+15551111111',
            'to_number': '+15552222222',
            'start_time': fields.Datetime.now(),
            'status': 'completed',
            'user_id': cls.rc_user.id,
            'ringcentral_call_id': 'sec-own-call',
        })
        cls.other_call = cls.env['ringcentral.call.history'].create({
            'config_id': cls.config.id,
            'direction': 'outbound',
            'from_number': '+15553333333',
            'to_number': '+15554444444',
            'start_time': fields.Datetime.now(),
            'status': 'completed',
            'user_id': cls.other_user.id,
            'ringcentral_call_id': 'sec-other-call',
        })

    def test_user_cannot_read_config(self):
        configs = self.env['ringcentral.config'].with_user(self.rc_user).search([])
        self.assertFalse(configs)

    def test_admin_can_read_config(self):
        configs = self.env['ringcentral.config'].with_user(self.admin_user).search([])
        self.assertIn(self.config, configs)

    def test_user_sees_own_call_history_only(self):
        calls = self.env['ringcentral.call.history'].with_user(self.rc_user).search([])
        self.assertEqual(calls, self.own_call)

    def test_admin_sees_all_call_history(self):
        calls = self.env['ringcentral.call.history'].with_user(self.admin_user).search([
            ('ringcentral_call_id', 'in', ['sec-own-call', 'sec-other-call']),
        ])
        self.assertEqual(len(calls), 2)

    def test_session_info_access_flags(self):
        info = self.env['res.users'].with_user(self.rc_user).get_ringcentral_session_info()
        self.assertTrue(info['has_access'])
        self.assertFalse(info['is_admin'])

        admin_info = self.env['res.users'].with_user(self.admin_user).get_ringcentral_session_info()
        self.assertTrue(admin_info['has_access'])
        self.assertTrue(admin_info['is_admin'])
