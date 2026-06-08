# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from datetime import date, timedelta
from odoo.tests.common import TransactionCase
from odoo import fields

class TestPettyCashVoucher(TransactionCase):

    def setUp(self):
        super(TestPettyCashVoucher, self).setUp()
        self.fund = self.env['petty.cash.fund'].create({
            'name': 'Test Fund',
            'journal_id': self.env['account.journal'].search([('type', '=', 'cash')], limit=1).id,
            'petty_cash_account_id': self.env['account.account'].search([('account_type', '=', 'asset_cash')], limit=1).id,
        })
        self.employee = self.env['hr.employee'].create({'name': 'Test Employee'})
        self.voucher = self.env['petty.cash.voucher'].create({
            'name': 'V/001',
            'fund_id': self.fund.id,
            'employee_id': self.employee.id,
            'amount': 100.0,
            'date': date.today() - timedelta(days=10),
        })

    def test_aging_computation(self):
        # Initial state is draft, aging should be 0
        self.voucher._compute_aging_fields()
        self.assertEqual(self.voucher.days_pending, 0)
        self.assertFalse(self.voucher.aging_bucket)

        # Change state to approved, aging should be 10
        self.voucher.state = 'approved'
        self.voucher._compute_aging_fields()
        self.assertEqual(self.voucher.days_pending, 10)
        self.assertEqual(self.voucher.aging_bucket, '8_15')

        # Change state to paid, but NOT reconciled, aging should still be 10 (FIXED)
        self.voucher.state = 'paid'
        self.voucher.is_reconciled = False
        self.voucher._compute_aging_fields()
        self.assertEqual(self.voucher.days_pending, 10)
        self.assertEqual(self.voucher.aging_bucket, '8_15')

        # Change state to paid AND reconciled, aging should be 0
        self.voucher.is_reconciled = True
        self.voucher._compute_aging_fields()
        self.assertEqual(self.voucher.days_pending, 0)
        self.assertFalse(self.voucher.aging_bucket)

    def test_aging_action_domain(self):
        # Verify domain includes paid unreconciled vouchers
        action = self.env.ref('petty_cash_management.action_petty_cash_aging')
        domain = action.domain
        
        # We can't easily test domain execution here without more setup, 
        # but we can check if it matches what we expect.
        self.assertIn("'is_reconciled', '=', False", domain)
        self.assertIn("'state', 'not in', ('draft', 'cancelled', 'rejected')", domain)
