# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PosProductComboLine(models.Model):
    _name = 'pos.product.combo.line'
    _description = 'POS Product Combo Line (direct lines on product)'

    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Combo Product',
        required=True,
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Component',
        required=True,
        domain=[('type', '!=', 'combo')],
        ondelete='restrict',
    )
    min_qty = fields.Float(string='Min Qty', digits='Product Unit of Measure', default=1.0)
    max_qty = fields.Float(string='Max Qty', digits='Product Unit of Measure', default=1.0)
    default_qty = fields.Float(string='Default Qty', digits='Product Unit of Measure', default=1.0)

    @api.constrains('product_id', 'product_tmpl_id')
    def _check_no_combo_in_combo(self):
        for line in self:
            if line.product_id.product_tmpl_id == line.product_tmpl_id:
                raise ValidationError(_('A combo product cannot contain itself.'))

    @api.constrains('min_qty', 'max_qty', 'default_qty')
    def _check_qty(self):
        for line in self:
            if line.min_qty < 0 or line.max_qty < 0 or line.default_qty < 0:
                raise ValidationError(_('Quantities must be positive.'))
            if line.max_qty < line.min_qty:
                raise ValidationError(_('Max Qty cannot be less than Min Qty.'))
            if not (line.min_qty <= line.default_qty <= line.max_qty):
                raise ValidationError(_('Default Qty must be between Min and Max Qty.'))
