# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero


class PosPayment(models.Model):
    _inherit = 'pos.payment'

    @api.constrains('amount')
    def _check_amount(self):
        if self.env.context.get('pos_order_cancel'):
            return
        return super()._check_amount()

    @api.constrains('payment_method_id')
    def _check_payment_method_id(self):
        if self.env.context.get('pos_order_cancel'):
            return
        return super()._check_payment_method_id()

    def _create_payment_moves(self, is_reverse=False):
        """When is_reverse and order has no invoice, use ref without account_move.name."""
        if not is_reverse:
            return super()._create_payment_moves(is_reverse=is_reverse)
        result = self.env['account.move']
        credit_line_ids = []
        change_payment = self.filtered(lambda p: p.is_change and p.payment_method_id.type == 'cash')
        payment_to_change = self.filtered(lambda p: not p.is_change and p.payment_method_id.type == 'cash')[:1]
        for payment in self - change_payment:
            order = payment.pos_order_id
            payment_method = payment.payment_method_id
            if payment_method.type == 'pay_later' or float_is_zero(payment.amount, precision_rounding=order.currency_id.rounding):
                continue
            accounting_partner = self.env["res.partner"]._find_accounting_partner(payment.partner_id)
            pos_session = order.session_id
            journal = pos_session.config_id.journal_id
            if change_payment and payment == payment_to_change:
                pos_payment_ids = payment.ids + change_payment.ids
                payment_amount = payment.amount + change_payment.amount
            else:
                pos_payment_ids = payment.ids
                payment_amount = payment.amount
            ref = _(
                'Invoice payment for %(order)s (%(account_move)s) using %(payment_method)s',
                order=order.name,
                account_move=order.account_move.name if order.account_move else _('Reversal'),
                payment_method=payment_method.name,
            )
            payment_move = self.env['account.move'].with_context(default_journal_id=journal.id).create({
                'journal_id': journal.id,
                'date': fields.Date.context_today(order, order.date_order),
                'ref': ref,
                'pos_payment_ids': pos_payment_ids,
            })
            result |= payment_move
            payment.write({'account_move_id': payment_move.id})
            amounts = pos_session._update_amounts({'amount': 0, 'amount_converted': 0}, {'amount': payment_amount}, payment.payment_date)
            credit_line_vals = pos_session._credit_amounts({
                'account_id': accounting_partner.with_company(order.company_id).property_account_receivable_id.id,
                'partner_id': accounting_partner.id,
                'move_id': payment_move.id,
            }, amounts['amount'], amounts['amount_converted'])
            is_split_transaction = payment.payment_method_id.split_transactions
            if is_split_transaction and is_reverse:
                reversed_move_receivable_account_id = accounting_partner.with_company(order.company_id).property_account_receivable_id.id
            elif is_reverse:
                reversed_move_receivable_account_id = payment.payment_method_id.receivable_account_id.id or self.company_id.account_default_pos_receivable_account_id.id
            else:
                reversed_move_receivable_account_id = self.company_id.account_default_pos_receivable_account_id.id
            debit_line_vals = pos_session._debit_amounts({
                'account_id': reversed_move_receivable_account_id,
                'move_id': payment_move.id,
                'partner_id': accounting_partner.id if is_split_transaction and is_reverse else False,
            }, amounts['amount'], amounts['amount_converted'])
            lines = self.env['account.move.line'].create([credit_line_vals, debit_line_vals])
            if amounts['amount_converted'] < 0:
                credit_line_ids += lines.filtered(lambda l: l.debit).ids
            else:
                credit_line_ids += lines.filtered(lambda l: l.credit).ids
            payment_move._post()
        return result.with_context(credit_line_ids=credit_line_ids)
