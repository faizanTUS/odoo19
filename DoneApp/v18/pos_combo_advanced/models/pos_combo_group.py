# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PosComboGroup(models.Model):
    _name = 'pos.combo.group'
    _description = 'POS Combo Group'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one('res.company', string='Company', index=True)
    line_ids = fields.One2many(
        'pos.combo.group.line',
        'group_id',
        string='Combo Lines',
        copy=True,
    )

    # Allow saving with no lines so user can: New → Name → Save, then edit to add Combo Lines.


class PosComboGroupLine(models.Model):
    _name = 'pos.combo.group.line'
    _description = 'POS Combo Group Line'

    group_id = fields.Many2one('pos.combo.group', required=True, ondelete='cascade')
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        domain=[('type', '!=', 'combo')],
        ondelete='restrict',
    )
    min_qty = fields.Float(string='Min Qty', digits='Product Unit of Measure', default=1.0)
    max_qty = fields.Float(string='Max Qty', digits='Product Unit of Measure', default=1.0)
    default_qty = fields.Float(string='Default Qty', digits='Product Unit of Measure', default=1.0)

    @api.constrains('min_qty', 'max_qty', 'default_qty')
    def _check_qty(self):
        for line in self:
            if line.min_qty < 0 or line.max_qty < 0 or line.default_qty < 0:
                raise ValidationError(_('Quantities must be positive.'))
            if line.max_qty < line.min_qty:
                raise ValidationError(_('Max Qty cannot be less than Min Qty.'))
            if not (line.min_qty <= line.default_qty <= line.max_qty):
                raise ValidationError(_('Default Qty must be between Min and Max Qty.'))

    @api.constrains('product_id')
    def _check_unique_in_group(self):
        for line in self:
            duplicates = self.search_count([
                ('group_id', '=', line.group_id.id),
                ('product_id', '=', line.product_id.id),
                ('id', '!=', line.id),  # Exclude self
            ])
            if duplicates > 0:
                raise ValidationError(_('Duplicate product "%s" in combo group "%s".') % (line.product_id.display_name,
                                                                                          line.group_id.name))
