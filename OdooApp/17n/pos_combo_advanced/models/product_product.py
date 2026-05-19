# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_combo_product = fields.Boolean(related='product_tmpl_id.is_combo_product', readonly=True)
    max_combo_items = fields.Integer(related='product_tmpl_id.max_combo_items', readonly=True)
    combo_display = fields.Selection(related='product_tmpl_id.combo_display', readonly=True)

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


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].extend([
            'is_combo_product',
            'max_combo_items',
            'combo_display',
        ])
        return result

    # 2️⃣ Inject combo options into loaded data
    def _get_pos_ui_product_product(self, params):
        products = super()._get_pos_ui_product_product(params)
        product_ids = [p['id'] for p in products if p.get('is_combo_product')]

        if product_ids:
            combo_products = self.env['product.product'].browse(product_ids)
            combo_map = {
                product.id: product._get_pos_combo_options()
                for product in combo_products
            }
            for product in products:
                if product['id'] in combo_map:
                    product['pos_combo_options'] = combo_map[product['id']]
                else:
                    product['pos_combo_options'] = []
        return products

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        if 'pos.combo.line' not in result:
            result.append('pos.combo.line')
        return result

    def _loader_params_pos_combo_line(self):
        return {
            "search_params": {
                "fields": [
                    "quantity",
                ],
            },
        }

    # 3️⃣ Provide data
    def _get_pos_ui_pos_combo_line(self, params):
        return self.env["pos.combo.line"].search_read(
            **params["search_params"]
        )
