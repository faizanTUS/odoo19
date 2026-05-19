# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from ast import literal_eval

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockBackdateWizard(models.TransientModel):
    _name = 'stock.backdate.wizard'
    _description = 'Mass Backdate Stock Operations'

    backdate = fields.Datetime(
        string='New Date',
        required=True,
        default=fields.Datetime.now,
        help="The new date to set for the selected stock operations."
    )

    backdate_reason = fields.Text(
        string='Reason for Backdate',
        required=True,
        help="Mandatory reason for auditing purposes."
    )

    picking_domain = fields.Char(
        string="Transfers Filter Domain",
        default=lambda self: self._default_picking_domain(),
        help="Odoo domain to filter the stock pickings to be backdated. E.g., [('state', '=', 'done'), ('date_done', '>', '2024-01-01')]"
    )

    recalculate_accounting = fields.Boolean(
        string='Recalculate Inventory Valuation',
        default=False,
        help="If checked, journal entry dates linked to stock moves will be updated to the backdate. Use with caution; reconciled entries are skipped."
    )

    @api.model
    def _default_picking_domain(self):
        """Pre-fill domain with selected transfer IDs when opened from list action."""
        active_ids = self.env.context.get('active_ids')
        if active_ids and self.env.context.get('active_model') == 'stock.picking':
            return str([('id', 'in', list(active_ids))])
        return "[('state', '=', 'done')]"

    def _parse_domain(self):
        """Parse picking_domain safely. Supports both string and list (from context default)."""
        self.ensure_one()
        domain = self.picking_domain
        if isinstance(domain, list):
            return domain
        if not (domain or domain.strip()):
            raise UserError(_("Transfers Filter Domain is required."))
        try:
            parsed = literal_eval(domain.strip())
            return list(parsed) if isinstance(parsed, (list, tuple)) else [parsed]
        except (ValueError, SyntaxError) as e:
            raise UserError(_("Invalid domain: %s") % str(e)) from e

    def action_mass_backdate(self):
        """Execute mass backdate: update picking/move dates and optionally linked journal entries."""
        self.ensure_one()

        domain = self._parse_domain()
        pickings = self.env['stock.picking'].search(domain)

        if not pickings:
            raise UserError(_("No stock transfers found matching the specified filter domain."))

        pickings_to_backdate = pickings.filtered(lambda p: p.state == 'done')
        if not pickings_to_backdate:
            raise UserError(_("None of the selected transfers are in the 'Done' state and eligible for backdating."))

        AccountMove = self.env['account.move'].sudo()
        has_stock_account = bool(self.env.get('stock.valuation.layer'))

        for picking in pickings_to_backdate:
            original_date_done = picking.date_done
            audit_vals = {
                'backdate_user_id': self.env.user.id,
                'backdate_reason': self.backdate_reason,
            }
            if not picking.original_date_done:
                audit_vals['original_date_done'] = original_date_done

            picking.write({
                'date_done': self.backdate,
                **audit_vals,
            })

            for move in picking.move_ids.filtered(lambda m: m.state == 'done'):
                move_vals = {'date': self.backdate}
                if not move.original_date:
                    move_vals['original_date'] = move.date
                move.write(move_vals)

                # Stock Move Line: update date so detailed operations reflect backdate
                if move.move_line_ids:
                    move.move_line_ids.write({'date': self.backdate})

                if self.recalculate_accounting and has_stock_account:
                    account_moves = AccountMove.search([('stock_move_id', '=', move.id), ('state', '=', 'posted')])
                    backdate_date = self.backdate.date() if hasattr(self.backdate, 'date') else self.backdate
                    for am in account_moves:
                        if am.line_ids.filtered('reconciled'):
                            continue
                        am.write({'date': backdate_date})

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('%s stock transfer(s) have been backdated to %s.') % (len(pickings_to_backdate), self.backdate),
                'sticky': False,
            }
        }
