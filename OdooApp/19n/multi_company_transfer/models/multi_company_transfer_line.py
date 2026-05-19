# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MultiCompanyTransferLine(models.Model):
    _name = 'multi.company.transfer.line'
    _description = 'Multi-Company Transfer Line'

    transfer_id = fields.Many2one(
        'multi.company.transfer',
        string='Transfer',
        required=True,
        ondelete='cascade',
        index=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    quantity = fields.Float(
        string='Quantity',
        required=True,
        digits='Product Unit of Measure',
        default=1.0,
    )
    available_qty = fields.Float(
        string='Available Quantity',
        digits='Product Unit of Measure',
        readonly=True,
        help='Quantity available in source location (set after Check Availability).',
    )
    done_qty = fields.Float(
        string='Done Quantity',
        digits='Product Unit of Measure',
        readonly=True,
        help='Quantity actually transferred (set when both pickings are done).',
    )
    product_uom_id = fields.Many2one(
        related='product_id.uom_id',
        string='UoM',
        readonly=True,
    )
    transfer_state = fields.Selection(
        related='transfer_id.state',
        string='Transfer Status',
        readonly=True,
    )

    @api.constrains('quantity')
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(
                    _('Quantity must be strictly positive for product %s.')
                    % line.product_id.display_name
                )

    @api.constrains('transfer_id', 'product_id')
    def _check_product_unique(self):
        for line in self:
            if line.transfer_id and line.product_id:
                same = line.transfer_id.stock_line_ids.filtered(
                    lambda l: l.product_id == line.product_id and l.id != line.id
                )
                if same:
                    raise ValidationError(
                        _('Product %s is already on a line of this transfer.')
                        % line.product_id.display_name
                    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            transfer_id = vals.get('transfer_id')
            if transfer_id:
                transfer = self.env['multi.company.transfer'].browse(transfer_id)
                if transfer.state != 'draft':
                    raise ValidationError(
                        _('Transfer lines can only be added in Draft state.')
                    )
        return super().create(vals_list)

    def unlink(self):
        for line in self:
            if line.transfer_id.state != 'draft':
                raise ValidationError(
                    _('Transfer lines can only be deleted in Draft state.')
                )
        return super().unlink()

    def write(self, vals):
        # Restrict editing product_id and quantity when transfer is not draft
        if 'product_id' in vals or 'quantity' in vals:
            for line in self:
                if line.transfer_id.state != 'draft':
                    raise ValidationError(
                        _('Transfer lines can only be modified in Draft state.')
                    )
        return super().write(vals)
