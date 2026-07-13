# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    combo_display = fields.Selection(
        [
            ('list', 'List View'),
            ('grid', 'Grid View'),
        ],
        string='Combo Display',
        default='list',
        help='Default display for combo product selection popup in POS (list or grid).',
    )

    def get_limited_products_loading(self, fields):
        result = super().get_limited_products_loading(fields)
        # Ensure advanced combo products are always loaded (they might be beyond LIMIT)
        base_domain = [
            ('active', '=', True),
            ('available_in_pos', '=', True),
            ('sale_ok', '=', True),
            ('product_tmpl_id.is_combo_product', '=', True),
        ]
        combo_products = self.env['product.product'].search(base_domain)
        loaded_ids = {p['id'] for p in result}
        missing = combo_products.filtered(lambda p: p.id not in loaded_ids)
        if missing:
            result = list(result) + missing.read(fields, load=False)
        return result
