# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo import _


class ProductComboItem(models.Model):
    _inherit = 'pos.combo.line'

    quantity = fields.Float(
        string='Quantity',
        digits='Product Unit of Measure',
        default=1.0,
        required=True,
    )

    @api.constrains('quantity')
    def _check_quantity_positive(self):
        for item in self:
            if item.quantity <= 0:
                raise ValidationError(_('Combo item quantity must be strictly positive.'))
