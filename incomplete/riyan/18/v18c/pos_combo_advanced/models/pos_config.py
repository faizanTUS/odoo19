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

    def _get_available_product_domain(self):
        domain = super()._get_available_product_domain()
        # Always include advanced combo products in POS so they appear in search/grid
        # even when "Restrict Categories" is enabled (they may have no POS category set)
        if self.limit_categories and self.iface_available_categ_ids:
            # Original domain ends with ('pos_categ_ids', 'in', ids).
            # Replace with: (is_combo_product OR pos_categ_ids in ...)
            categ_ids = self._get_available_categories().ids
            domain = domain[:-1] + [
                '|',
                ('product_tmpl_id.is_combo_product', '=', True),
                ('pos_categ_ids', 'in', categ_ids),
            ]
        return domain

    def get_limited_products_loading(self, fields):
        result = super().get_limited_products_loading(fields)
        # Ensure advanced combo products are always loaded (they might be beyond LIMIT)
        base_domain = [
            *self.env['product.product']._check_company_domain(self.company_id),
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
