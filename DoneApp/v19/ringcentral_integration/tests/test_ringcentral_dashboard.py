# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestRingCentralDashboard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Dashboard = cls.env['ringcentral.dashboard']
        cls.CallHistory = cls.env['ringcentral.call.history']
        cls.config = cls.env['ringcentral.config'].create({
            'name': 'Dashboard Test Config',
            'client_id': 'dash_client',
            'client_secret': 'dash_secret',
        })
        cls.admin_user = cls.env.ref('base.user_admin')
        cls.admin_user.write({
            'group_ids': [(4, cls.env.ref('ringcentral_integration.group_ringcentral_admin').id)],
        })
        cls.user_a = cls.env['res.users'].create({
            'name': 'RC User A',
            'login': 'rc_user_a_dashboard@test.com',
            'group_ids': [(4, cls.env.ref('ringcentral_integration.group_ringcentral_user').id)],
        })
        cls.user_b = cls.env['res.users'].create({
            'name': 'RC User B',
            'login': 'rc_user_b_dashboard@test.com',
            'group_ids': [(4, cls.env.ref('ringcentral_integration.group_ringcentral_user').id)],
        })
        cls._call_seq = 0
        cls.partner = cls.env['res.partner'].create({
            'name': 'Dashboard Contact',
            'phone': '+15550001111',
        })
        now = fields.Datetime.now()
        today = now.replace(hour=10, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)

        cls._create_call(
            direction='inbound',
            status='completed',
            start_time=today,
            duration=120,
            user_id=cls.user_a.id,
            from_partner_id=cls.partner.id,
        )
        cls._create_call(
            direction='outbound',
            status='answered',
            start_time=today,
            duration=60,
            user_id=cls.user_a.id,
        )
        cls._create_call(
            direction='inbound',
            status='no-answer',
            start_time=today,
            duration=0,
            user_id=cls.user_b.id,
        )
        cls._create_call(
            direction='outbound',
            status='failed',
            start_time=yesterday,
            duration=0,
            user_id=cls.user_b.id,
        )
        cls._create_call(
            direction='inbound',
            status='ringing',
            start_time=today,
            duration=0,
            user_id=cls.user_a.id,
        )

    @classmethod
    def _create_call(cls, **kwargs):
        cls._call_seq += 1
        values = {
            'config_id': cls.config.id,
            'direction': 'inbound',
            'from_number': '+15550001111',
            'to_number': '+15550002222',
            'start_time': fields.Datetime.now(),
            'status': 'completed',
            'duration': 30,
            'ringcentral_call_id': f'dash-test-{cls._call_seq}',
        }
        values.update(kwargs)
        user_id = values.pop('user_id', None)
        if user_id:
            if values.get('direction') == 'outbound':
                values.setdefault('initiated_by_id', user_id)
            else:
                values.setdefault('answered_by_id', user_id)
        return cls.CallHistory.create(values)

    def _dashboard_as(self, user, filters=None):
        return self.Dashboard.with_user(user).get_dashboard_data(filters or {'date_preset': 'this_month'})

    def test_dashboard_structure(self):
        data = self._dashboard_as(self.admin_user)
        self.assertIn('kpis', data)
        self.assertIn('charts', data)
        self.assertIn('analytics', data)
        self.assertIn('filter_options', data)
        self.assertTrue(data['kpis'])
        self.assertIn('call_trend', data['charts'])
        self.assertIn('success_rate', data['analytics'])

    def test_kpis_include_action_domains(self):
        data = self._dashboard_as(self.admin_user)
        for kpi in data['kpis']:
            self.assertIn('action_domain', kpi)
            self.assertIsInstance(kpi['action_domain'], list)
            self.assertIn('key', kpi)
            self.assertIn('value', kpi)

    def test_total_calls_count(self):
        data = self._dashboard_as(self.admin_user, {'date_preset': 'this_month'})
        total_kpi = next(k for k in data['kpis'] if k['key'] == 'total_calls')
        self.assertEqual(int(total_kpi['value']), 5)

    def test_direction_filter(self):
        data = self._dashboard_as(self.admin_user, {
            'date_preset': 'this_month',
            'direction': 'inbound',
        })
        total_kpi = next(k for k in data['kpis'] if k['key'] == 'total_calls')
        self.assertEqual(int(total_kpi['value']), 3)

    def test_status_filter(self):
        data = self._dashboard_as(self.admin_user, {
            'date_preset': 'this_month',
            'status': 'completed',
        })
        total_kpi = next(k for k in data['kpis'] if k['key'] == 'total_calls')
        self.assertEqual(int(total_kpi['value']), 1)

    def test_user_filter(self):
        data = self._dashboard_as(self.admin_user, {
            'date_preset': 'this_month',
            'user_id': self.user_b.id,
        })
        total_kpi = next(k for k in data['kpis'] if k['key'] == 'total_calls')
        self.assertEqual(int(total_kpi['value']), 2)

    def test_record_rule_user_scoping(self):
        data = self._dashboard_as(self.user_a, {'date_preset': 'this_month'})
        total_kpi = next(k for k in data['kpis'] if k['key'] == 'total_calls')
        self.assertEqual(int(total_kpi['value']), 3)

    def test_filter_options_admin(self):
        options = self.Dashboard.with_user(self.admin_user).get_filter_options()
        self.assertTrue(options['is_admin'])
        self.assertTrue(options['can_filter_users'])
        self.assertTrue(any(u['id'] == self.user_a.id for u in options['users']))
        self.assertTrue(any(u['id'] == self.user_b.id for u in options['users']))

    def test_filter_users_from_rc_groups_without_call_user_id(self):
        """Users appear in filter even when call records have no user_id."""
        self.CallHistory.create({
            'config_id': self.config.id,
            'direction': 'inbound',
            'from_number': '+15559998888',
            'to_number': '+15559997777',
            'start_time': fields.Datetime.now(),
            'status': 'completed',
            'duration': 10,
            'ringcentral_call_id': 'dash-no-user-id',
        })
        options = self.Dashboard.with_user(self.admin_user).get_filter_options()
        user_ids = [u['id'] for u in options['users']]
        self.assertIn(self.user_a.id, user_ids)
        self.assertIn(self.user_b.id, user_ids)

    def test_filter_sanitization_for_user(self):
        data = self._dashboard_as(self.user_a, {
            'date_preset': 'this_month',
            'user_id': self.user_b.id,
        })
        total_kpi = next(k for k in data['kpis'] if k['key'] == 'total_calls')
        self.assertEqual(int(total_kpi['value']), 3)

    def test_admin_top_users_chart_hidden_for_user(self):
        data = self._dashboard_as(self.user_a, {'date_preset': 'this_month'})
        self.assertEqual(data['charts']['top_users']['labels'], [])
        self.assertEqual(data['analytics']['top_agents'], [])

    def test_admin_top_users_chart_for_admin(self):
        data = self._dashboard_as(self.admin_user, {'date_preset': 'this_month'})
        self.assertTrue(data['charts']['top_users']['labels'])
