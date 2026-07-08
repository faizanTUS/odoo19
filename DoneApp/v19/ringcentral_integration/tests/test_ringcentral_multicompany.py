# -*- coding: utf-8 -*-

from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestRingCentralMultiCompany(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_a = cls.env.company
        cls.company_b = cls.env['res.company'].create({'name': 'RC Test Company B'})

    def test_company_specific_config_resolution(self):
        config_a = self.env['ringcentral.config'].create({
            'name': 'Company A Config',
            'client_id': 'client_a',
            'client_secret': 'secret_a',
            'company_ids': [(6, 0, [self.company_a.id])],
        })
        config_b = self.env['ringcentral.config'].create({
            'name': 'Company B Config',
            'client_id': 'client_b',
            'client_secret': 'secret_b',
            'company_ids': [(6, 0, [self.company_b.id])],
        })
        resolved_a = self.env['ringcentral.config']._get_company_active_config(self.company_a)
        resolved_b = self.env['ringcentral.config']._get_company_active_config(self.company_b)
        self.assertEqual(resolved_a, config_a)
        self.assertEqual(resolved_b, config_b)

    def test_global_config_fallback(self):
        global_config = self.env['ringcentral.config'].create({
            'name': 'Global Config',
            'client_id': 'global_client',
            'client_secret': 'global_secret',
        })
        resolved = self.env['ringcentral.config']._get_company_active_config(self.company_a)
        self.assertEqual(resolved, global_config)

    def test_multiple_configs_same_company_allowed(self):
        first = self.env['ringcentral.config'].create({
            'name': 'First Config',
            'client_id': 'first_client',
            'client_secret': 'first_secret',
            'company_ids': [(6, 0, [self.company_a.id])],
        })
        second = self.env['ringcentral.config'].create({
            'name': 'Second Config',
            'client_id': 'second_client',
            'client_secret': 'second_secret',
            'company_ids': [(6, 0, [self.company_a.id])],
        })
        configs = self.env['ringcentral.config']._get_company_configs(self.company_a)
        self.assertIn(first, configs)
        self.assertIn(second, configs)
        self.assertEqual(len(configs), 2)

    def test_new_config_auto_assigns_active_company(self):
        config = self.env['ringcentral.config'].create({
            'name': 'Auto Company Config',
            'client_id': 'auto_client',
            'client_secret': 'auto_secret',
        })
        self.assertIn(self.company_a, config.company_ids)

    def test_call_history_company_from_config(self):
        config = self.env['ringcentral.config'].create({
            'name': 'History Company Config',
            'client_id': 'hist_client',
            'client_secret': 'hist_secret',
            'company_ids': [(6, 0, [self.company_b.id])],
        })
        call = self.env['ringcentral.call.history'].create({
            'config_id': config.id,
            'direction': 'inbound',
            'from_number': '+15556667777',
            'to_number': '+15558889999',
            'start_time': self.env['ringcentral.call.history']._fields['start_time'].default(),
            'status': 'completed',
            'ringcentral_call_id': 'mc-call-1',
        })
        self.assertEqual(call.company_id, self.company_b)
