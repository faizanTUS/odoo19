# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round, float_is_zero

_logger = logging.getLogger(__name__)


class PosOrderCancelWizard(models.TransientModel):
    _name = 'pos.order.cancel.wizard'
    _description = 'Cancel POS Order Wizard'

    cancellation_method = fields.Selection(
        selection=[
            ('cancel_only', 'Cancel only'),
            ('reset_draft', 'Cancel and Reset to Draft'),
            ('delete', 'Cancel and Delete'),
        ],
        string='Cancellation Method',
        required=True,
        default='cancel_only',
        help="Cancel only: orders stay in Cancelled state (form shows Cancelled). "
             "Cancel and Reset to Draft: orders are cancelled then reset to draft (form shows New). "
             "Cancel and Delete: orders are cancelled then deleted.",
    )
    cancel_delivery_order = fields.Boolean(
        string='Cancel Delivery Order',
        default=False,
        help="When you want to cancel POS orders and delivery orders then you can choose this option.",
    )
    cancel_invoice = fields.Boolean(
        string='Cancel Invoice',
        default=False,
        help="When you want to cancel POS orders and invoice then you can choose this option.",
    )
    pos_order_ids = fields.Many2many(
        comodel_name='pos.order',
        string='POS Orders',
        relation='pos_order_cancel_wizard_order_rel',
        column1='wizard_id',
        column2='order_id',
        required=True,
        help="POS orders to cancel.",
    )

    def _create_payment_reversals(self, orders):
        """Create negative pos.payment entries and their reverse moves; reconcile receivable lines."""
        PosPayment = self.env['pos.payment'].sudo().with_context(pos_order_cancel=True)
        for order in orders:
            to_reverse = order.payment_ids.filtered(
                lambda p: p.amount > 0
                and p.payment_method_id.type != 'pay_later'
                and not float_is_zero(p.amount, precision_rounding=order.currency_id.rounding)
            )
            if not to_reverse:
                continue
            new_payments = PosPayment.browse()
            for payment in to_reverse:
                new_payments |= PosPayment.with_company(order.company_id).create({
                    'pos_order_id': order.id,
                    'payment_method_id': payment.payment_method_id.id,
                    'amount': -payment.amount,
                    'payment_date': fields.Datetime.now(),
                })
            if new_payments:
                try:
                    new_payments.with_company(order.company_id)._create_payment_moves(is_reverse=True)
                    self._reconcile_payment_reversals(order)
                except Exception as e:
                    _logger.warning(
                        'POS Cancel Wizard: could not create payment reversal for order %s: %s',
                        order.name, e,
                        exc_info=True
                    )

    def _reconcile_payment_reversals(self, order):
        """Reconcile receivable lines from original payment moves with reversal moves."""
        if not order.partner_id:
            return
        receivable_account = self.env['res.partner']._find_accounting_partner(order.partner_id).with_company(order.company_id).property_account_receivable_id
        if not receivable_account or not receivable_account.reconcile:
            return
        original_moves = order.payment_ids.filtered(lambda p: p.amount > 0).mapped('account_move_id')
        reversal_moves = order.payment_ids.filtered(lambda p: p.amount < 0).mapped('account_move_id')
        if not original_moves or not reversal_moves:
            return
        receivable_lines = (original_moves | reversal_moves).mapped('line_ids').filtered(
            lambda l: l.account_id == receivable_account and l.partner_id and not l.reconciled
        )
        if receivable_lines:
            receivable_lines.with_company(order.company_id).reconcile()

    def _cancel_done_picking(self, picking):
        """Reverse stock and set a done delivery order to cancelled state (single entry, no return picking).
        Returns (True, None) on success, (False, error_message) on failure."""
        self.ensure_one()
        if picking.state != 'done':
            return (False, _('Picking is not in Done state.'))
        StockQuant = self.env['stock.quant'].sudo()
        try:
            with self.env.cr.savepoint():
                self._cancel_done_picking_impl(picking, StockQuant)
        except Exception as e:
            err_msg = str(e) if str(e) else repr(e)
            _logger.warning(
                'POS Cancel Wizard: could not cancel done picking %s: %s',
                picking.name, e,
                exc_info=True
            )
            return (False, err_msg)
        return (True, None)

    def _cancel_done_picking_impl(self, picking, StockQuant):
        """Implementation of cancel done picking (inside savepoint)."""
        cancel_ctx = {'pos_order_cancel_done_picking': True}
        for move in picking.move_ids.filtered(lambda m: m.state == 'done' and not m.scrapped):
            qty_done = move.quantity
            if float_is_zero(qty_done, precision_rounding=move.product_uom.rounding):
                move.with_context(**cancel_ctx).move_line_ids.unlink()
                move.sudo().write({'state': 'cancel', 'picked': False})
                continue
            if getattr(move.product_id, 'is_storable', True):
                if move.move_line_ids:
                    for ml in move.move_line_ids:
                        if float_is_zero(ml.quantity, precision_rounding=ml.product_uom_id.rounding):
                            continue
                        StockQuant._update_available_quantity(
                            ml.product_id,
                            ml.location_dest_id,
                            -ml.quantity,
                            lot_id=ml.lot_id,
                            package_id=ml.result_package_id,
                            owner_id=ml.owner_id,
                        )
                        StockQuant._update_available_quantity(
                            ml.product_id,
                            ml.location_id,
                            ml.quantity,
                            lot_id=ml.lot_id,
                            package_id=ml.package_id,
                            owner_id=ml.owner_id,
                        )
                else:
                    StockQuant._update_available_quantity(
                        move.product_id,
                        move.location_dest_id,
                        -qty_done,
                        lot_id=False,
                        package_id=False,
                        owner_id=False,
                    )
                    StockQuant._update_available_quantity(
                        move.product_id,
                        move.location_id,
                        qty_done,
                        lot_id=False,
                        package_id=False,
                        owner_id=False,
                    )
            move.with_context(**cancel_ctx).move_line_ids.unlink()
            move.sudo().write({'state': 'cancel', 'picked': False})
        self.env.flush_all()
        picking.invalidate_recordset(['state'])
        picking._compute_state()

    def action_confirm(self):
        self.ensure_one()
        orders = self.pos_order_ids.filtered(lambda o: o.state != 'cancel')
        if not orders:
            raise UserError(_('No orders to cancel. Selected orders are already cancelled.'))

        pickings_to_cancel = self.env['stock.picking']
        pickings_failed = self.env['stock.picking']
        invoices_to_cancel = self.env['account.move']
        if self.cancel_delivery_order:
            pickings_direct = orders.mapped('picking_ids')
            procurement_groups = orders.mapped('procurement_group_id').filtered(None)
            pickings_via_group = self.env['stock.picking']
            if procurement_groups:
                pickings_via_group = self.env['stock.picking'].search([
                    ('group_id', 'in', procurement_groups.ids)
                ])
            all_pickings = (pickings_direct | pickings_via_group)
            pickings_to_cancel = all_pickings.filtered(lambda p: p.state != 'cancel')
        if self.cancel_invoice:
            invoices_to_cancel = orders.mapped('account_move').filtered(
                lambda m: m.exists() and m.state not in ('cancel',)
            )

        if invoices_to_cancel:
            for inv in invoices_to_cancel:
                try:
                    inv.sudo().button_cancel()
                except Exception as e:
                    _logger.warning(
                        'POS Cancel Wizard: could not cancel invoice %s: %s',
                        inv.name, e
                    )
                    raise UserError(
                        _('Could not cancel invoice %(name)s: %(reason)s')
                        % {'name': inv.name, 'reason': str(e)}
                    ) from e

        if pickings_to_cancel:
            for picking in pickings_to_cancel:
                try:
                    picking.sudo().action_cancel()
                except UserError as e:
                    _logger.warning(
                        'POS Cancel Wizard: could not cancel picking %s: %s',
                        picking.name, e
                    )
                    pickings_failed |= picking

        if self.cancellation_method in ('cancel_only', 'reset_draft'):
            orders_with_payments = orders.filtered(lambda o: o.payment_ids)
            if orders_with_payments:
                try:
                    with self.env.cr.savepoint():
                        self._create_payment_reversals(orders_with_payments)
                except Exception as rev_e:
                    _logger.error(
                        "POS Cancel Wizard: Payment reversal FAILED (isolated) for orders %s - continuing wizard. Error: %s",
                        ', '.join(orders_with_payments.mapped('name')),
                        rev_e,
                        exc_info=True
                    )
                    pass

        orders.with_context(pos_order_cancel=True).write({'state': 'cancel'})

        if self.cancellation_method == 'cancel_only':
            pass
        elif self.cancellation_method == 'reset_draft':
            if self.cancel_invoice and invoices_to_cancel:
                orders.with_context(pos_order_cancel=True).write({
                    'state': 'draft',
                    'account_move': False,
                })
            else:
                orders.with_context(pos_order_cancel=True).write({'state': 'draft'})
        else:
            for order in orders:
                order.payment_ids.sudo().unlink()
            orders.sudo().unlink()

        pickings_cancelled = self.env['stock.picking']
        pickings_failed_reasons = []
        if pickings_failed:
            for picking in pickings_failed.filtered(lambda p: p.state == 'done'):
                ok, err = self._cancel_done_picking(picking)
                if ok:
                    pickings_cancelled |= picking
                else:
                    pickings_failed_reasons.append((picking.name, err or _('Unknown error')))
            for picking in pickings_failed.filtered(lambda p: p.state != 'done'):
                pickings_failed_reasons.append((picking.name, _('Not in Done state.')))

        if pickings_cancelled:
            names = ', '.join(pickings_cancelled.mapped('name'))
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'sticky': False,
                    'message': _(
                        'Delivery order(s) set to Cancelled (same entry, no new picking): %(names)s.'
                    ) % {'names': names},
                    'next': {'type': 'ir.actions.act_window_close'},
                },
            }
        if pickings_failed_reasons:
            details = '; '.join('%s: %s' % (name, reason) for name, reason in pickings_failed_reasons)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'sticky': True,
                    'message': _(
                        'Delivery order(s) could not be set to Cancelled: %(details)s. '
                        'Check server log for details, or create a return from Inventory.'
                    ) % {'details': details},
                    'next': {'type': 'ir.actions.act_window_close'},
                },
            }
        if pickings_failed:
            names = ', '.join(pickings_failed.mapped('name'))
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'sticky': False,
                    'message': _(
                        '%(count)s delivery order(s) could not be cancelled: %(names)s.'
                    ) % {'count': len(pickings_failed), 'names': names},
                    'next': {'type': 'ir.actions.act_window_close'},
                },
            }
        return {'type': 'ir.actions.act_window_close'}
