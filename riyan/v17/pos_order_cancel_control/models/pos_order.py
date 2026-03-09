# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def write(self, vals):
        # Allow cancel wizard to transition paid/done/invoiced orders to cancel/draft
        if self.env.context.get('pos_order_cancel') and vals.get('state') in ('cancel', 'draft'):
            allowed_vals = ['paid', 'done', 'invoiced']
            if any(o.state in allowed_vals for o in self):
                # Bypass standard restriction: call base Model.write to avoid UserError
                return models.Model.write(self, vals)
        return super().write(vals)

    def action_cancel_pos_orders_wizard(self):
        """Open the Cancel POS Order wizard for selected orders."""
        if not self:
            raise UserError(_('Please select at least one POS order.'))
        already_cancelled = self.filtered(lambda o: o.state == 'cancel')
        if already_cancelled:
            raise UserError(
                _('The following orders are already cancelled: %s')
                % ', '.join(already_cancelled.mapped('name'))
            )
        return {
            'name': _('Cancel POS Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'pos.order.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_pos_order_ids': [(6, 0, self.ids)],
                'active_ids': self.ids,
            },
        }
