# -*- coding: utf-8 -*-
from unittest.mock import patch

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestRingCentralContactSync(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Sync = cls.env['ringcentral.contact.sync']
        cls.config = cls.env['ringcentral.config'].create({
            'name': 'Contact Sync Config',
            'client_id': 'sync_client',
            'client_secret': 'sync_secret',
            'access_token': 'test-token',
            'token_expires_at': '2099-01-01 00:00:00',
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Old Partner Name',
            'phone': '+17145550111',
        })

    def _rc_contact(self, **kwargs):
        base = {
            'id': 101,
            'firstName': 'Jane',
            'lastName': 'Doe',
            'company': 'Acme Corp',
            'email': 'jane.doe@example.com',
            'mobilePhone': '+17145550111',
            'businessPhone': '+17145550222',
            'jobTitle': 'Director',
            'notes': 'VIP customer',
            'businessAddress': {
                'street': '100 Market St',
                'city': 'San Francisco',
                'zip': '94105',
                'state': 'California',
                'country': 'US',
            },
        }
        base.update(kwargs)
        return base

    def test_fetch_address_book_contacts_paginates(self):
        pages = [
            {
                'records': [self._rc_contact(id=1)],
                'paging': {'page': 1, 'totalPages': 2},
            },
            {
                'records': [self._rc_contact(id=2)],
                'paging': {'page': 2, 'totalPages': 2},
            },
        ]

        def fake_request(method, endpoint, data=None, params=None, parse_json=True):
            self.assertEqual(endpoint, '/account/~/extension/~/address-book/contact')
            return pages[(params or {}).get('page', 1) - 1]

        with patch.object(type(self.config), '_make_api_request', side_effect=fake_request):
            records = self.Sync.fetch_address_book_contacts(self.config)
        self.assertEqual(len(records), 2)

    def test_sync_enriches_partner_fill_only(self):
        rc_record = self._rc_contact()
        with patch.object(type(self.config), '_make_api_request') as mock_api:
            mock_api.return_value = {
                'records': [rc_record],
                'paging': {'page': 1, 'totalPages': 1},
            }
            counters = self.Sync.sync_contacts(self.config)

        self.assertEqual(counters['processed'], 1)
        self.assertEqual(counters['partners_updated'], 1)
        self.assertEqual(counters['skipped'], 0)
        self.assertEqual(self.partner.name, 'Old Partner Name')
        self.assertEqual(self.partner.email, 'jane.doe@example.com')
        self.assertEqual(self.partner.phone, '+17145550111')
        self.assertEqual(self.partner.company_name, 'Acme Corp')
        self.assertEqual(self.partner.function, 'Director')
        self.assertTrue(self.config.last_contact_sync)

    def test_sync_overwrite_updates_existing_partner_fields(self):
        self.config.contact_sync_overwrite = True
        rc_record = self._rc_contact()
        with patch.object(type(self.config), '_make_api_request') as mock_api:
            mock_api.return_value = {
                'records': [rc_record],
                'paging': {'page': 1, 'totalPages': 1},
            }
            self.Sync.sync_contacts(self.config)
        self.assertEqual(self.partner.name, 'Jane Doe')

    def test_sync_skips_unmatched_contact_without_creating_partner(self):
        rc_record = self._rc_contact(mobilePhone='+19998887777', businessPhone='')
        partner_count_before = self.env['res.partner'].search_count([])
        with patch.object(type(self.config), '_make_api_request') as mock_api:
            mock_api.return_value = {
                'records': [rc_record],
                'paging': {'page': 1, 'totalPages': 1},
            }
            counters = self.Sync.sync_contacts(self.config)
        self.assertEqual(counters['skipped'], 1)
        self.assertEqual(counters['partners_updated'], 0)
        self.assertEqual(self.env['res.partner'].search_count([]), partner_count_before)

    def test_sync_counts_failed_record(self):
        good = self._rc_contact(id=201)
        bad = self._rc_contact(id=202, mobilePhone='+17145550333', businessPhone='')
        self.env['res.partner'].create({'name': 'Another Partner', 'phone': '+17145550333'})
        original_normalize = type(self.Sync).normalize_rc_contact

        @classmethod
        def normalize_with_failure(cls, rc_record):
            if rc_record.get('id') == 202:
                raise ValueError('forced failure')
            return original_normalize.__func__(cls, rc_record)

        with patch.object(type(self.config), '_make_api_request') as mock_api, patch.object(
            type(self.Sync), 'normalize_rc_contact', new=normalize_with_failure,
        ):
            mock_api.return_value = {
                'records': [good, bad],
                'paging': {'page': 1, 'totalPages': 1},
            }
            counters = self.Sync.sync_contacts(self.config)
        self.assertEqual(counters['processed'], 2)
        self.assertEqual(counters['failed'], 1)
        self.assertEqual(counters['partners_updated'], 1)

    def test_push_single_config_on_partner_save(self):
        with patch.object(type(self.config), '_make_api_request') as mock_api:
            mock_api.return_value = {'id': 555}
            self.config.push_contacts_to_ringcentral = True
            partner = self.env['res.partner'].create({
                'name': 'Push Partner',
                'phone': '+17145550999',
                'email': 'push@example.com',
            })
        mock_api.assert_called()
        link = self.env['ringcentral.partner.contact.link'].search([
            ('partner_id', '=', partner.id),
            ('config_id', '=', self.config.id),
        ])
        self.assertEqual(len(link), 1)
        self.assertEqual(link.ringcentral_contact_id, '555')

    def test_push_skipped_when_boolean_disabled(self):
        partner = self.env['res.partner'].create({
            'name': 'No Push Partner',
            'phone': '+17145550888',
        })
        with patch.object(type(self.config), '_make_api_request') as mock_api:
            partner.write({'email': 'nopush@example.com'})
        mock_api.assert_not_called()

    def test_push_requires_partner_config_when_multiple_accounts(self):
        second = self.env['ringcentral.config'].create({
            'name': 'Second Contact Config',
            'client_id': 'second_sync',
            'client_secret': 'second_secret',
            'access_token': 'token-2',
            'token_expires_at': '2099-01-01 00:00:00',
            'company_ids': [(6, 0, [self.env.company.id])],
            'push_contacts_to_ringcentral': True,
        })
        self.config.push_contacts_to_ringcentral = True
        partner = self.env['res.partner'].create({
            'name': 'Multi Config Partner',
            'phone': '+17145550777',
        })
        self.assertTrue(partner.ringcentral_multi_config)
        with patch.object(type(self.config), '_make_api_request') as mock_api:
            partner.write({'email': 'multi@example.com'})
        mock_api.assert_not_called()

        with patch.object(type(second), '_make_api_request', return_value={'id': 777}) as mock_second:
            partner.write({'ringcentral_config_id': second.id})
        mock_second.assert_called()
        link = self.env['ringcentral.partner.contact.link'].search([
            ('partner_id', '=', partner.id),
            ('config_id', '=', second.id),
        ])
        self.assertEqual(link.ringcentral_contact_id, '777')

    def test_inbound_sync_does_not_trigger_outbound_push(self):
        self.config.push_contacts_to_ringcentral = True
        rc_record = self._rc_contact()
        with patch.object(type(self.config), '_make_api_request') as mock_api:
            mock_api.return_value = {
                'records': [rc_record],
                'paging': {'page': 1, 'totalPages': 1},
            }
            self.Sync.with_context(ringcentral_skip_push=True).sync_contacts(self.config)
            post_calls = [
                call for call in mock_api.call_args_list
                if call.args and call.args[0] == 'POST'
            ]
            put_calls = [
                call for call in mock_api.call_args_list
                if call.args and call.args[0] == 'PUT'
            ]
        self.assertFalse(post_calls)
        self.assertFalse(put_calls)

    def test_contact_cron_calls_sync(self):
        self.config.last_contact_sync = False
        with patch.object(type(self.Sync), 'sync_contacts') as mock_sync:
            self.config.sync_contacts_recent()
        mock_sync.assert_called_once_with(self.config)

    def test_contact_cron_skips_recent_sync(self):
        from odoo import fields
        from datetime import timedelta
        self.config.last_contact_sync = fields.Datetime.now()
        with patch.object(type(self.Sync), 'sync_contacts') as mock_sync:
            self.config.sync_contacts_recent()
        mock_sync.assert_not_called()
