# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_combo_product = fields.Boolean(related='product_tmpl_id.is_combo_product', readonly=True)
    max_combo_items = fields.Integer(related='product_tmpl_id.max_combo_items', readonly=True)
    combo_display = fields.Selection(related='product_tmpl_id.combo_display', readonly=True)

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        extra = ['is_combo_product', 'max_combo_items', 'combo_display']
        for f in extra:
            if f not in fields:
                fields = list(fields) + [f]
        return fields

    def _get_pos_combo_options(self):
        """Return list of combo options for this product (variant). Used for POS load."""
        self.ensure_one()
        if not self.is_combo_product:
            return []
        tmpl = self.product_tmpl_id
        options = []
        # Direct lines
        for line in tmpl.pos_combo_line_ids:
            options.append({
                'product_id': line.product_id.id,
                'min_qty': line.min_qty,
                'max_qty': line.max_qty,
                'default_qty': line.default_qty,
                'group_name': False,
            })
        # From groups
        for group in tmpl.pos_combo_group_ids:
            for line in group.line_ids:
                options.append({
                    'product_id': line.product_id.id,
                    'min_qty': line.min_qty,
                    'max_qty': line.max_qty,
                    'default_qty': line.default_qty,
                    'group_name': group.name,
                })
        return options

    def _load_pos_data(self, data):
        result = super()._load_pos_data(data)
        # Inject pos_combo_options for combo products
        for product in result.get('data', []):
            if product.get('is_combo_product'):
                prod = self.browse(product['id'])
                product['pos_combo_options'] = prod._get_pos_combo_options()
        return result
