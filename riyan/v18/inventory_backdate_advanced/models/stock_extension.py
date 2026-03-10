# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    original_date_done = fields.Datetime(
        string='Original Date Done',
        readonly=True,
        help="The original date the transfer was marked as done, before any backdating."
    )

    backdate_user_id = fields.Many2one(
        'res.users',
        string='Backdated By',
        readonly=True,
        help="The user who performed the backdate operation."
    )

    backdate_reason = fields.Text(
        string='Backdate Reason',
        readonly=True,
        help="Reason provided for the backdate operation."
    )

    @api.model_create_multi
    def create(self, vals_list):
        # Set original_date_done on creation if date_done is present
        for vals in vals_list:
            if 'date_done' in vals and vals.get('date_done'):
                vals['original_date_done'] = vals['date_done']
        return super().create(vals_list)

    def write(self, vals):
        if 'date_done' in vals and vals.get('date_done'):
            for picking in self:
                pvals = dict(vals)
                if not picking.original_date_done:
                    pvals['original_date_done'] = picking.date_done or vals['date_done']
                super(StockPicking, picking).write(pvals)
            return True
        return super().write(vals)

class StockMove(models.Model):
    _inherit = 'stock.move'

    original_date = fields.Datetime(
        string='Original Date',
        readonly=True,
        help="The original date the stock move was done, before any backdating."
    )

    @api.model_create_multi
    def create(self, vals_list):
        # Set original_date on creation if date is present
        for vals in vals_list:
            if 'date' in vals and vals.get('date'):
                vals['original_date'] = vals['date']
        return super().create(vals_list)

    def write(self, vals):
        if 'date' in vals and vals.get('date'):
            for move in self:
                mvals = dict(vals)
                if not move.original_date:
                    mvals['original_date'] = move.date or vals['date']
                super(StockMove, move).write(mvals)
            return True
        return super().write(vals)
