# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    model_name = fields.Char("Model Name")

    @api.constrains('model_name')
    def _check_unique_invoice_ref(self):
        for record in self:
            if record.model_name:
                duplicate = self.search([('id', '!=', record.id), ('model_name', '=', record.model_name)], limit=1)
                if duplicate:
                    raise ValidationError(
                        f"The Product with this Model - {record.model_name} already exist. \n please enter new Model Name."
                    )

    @api.model
    def get_all_variants_info(self, template_id):
        """Return variant lines with attributes, internal stock, and list price for a product template."""
        template = self.browse(template_id)
        variants = template.product_variant_ids
        qty_by_variant = self._internal_qty_by_variant(variants.ids)
        variants_info = []

        for variant in variants:
            parts = []
            for ptav in variant.product_template_attribute_value_ids:
                parts.append(f"{ptav.attribute_id.name}: {ptav.product_attribute_value_id.name}")

            variants_info.append({
                'variant_id': variant.id,
                'display_name': variant.display_name,
                'attributes_display': ", ".join(parts),
                'qty_available': qty_by_variant.get(variant.id, 0.0),
                'list_price': variant.list_price,
                'wsp_price': variant.list_price,
            })

        return {
            "image_128": template.image_128,
            "product_name": template.name,
            "variants": variants_info,
        }

    def _internal_qty_by_variant(self, variant_ids):
        """Sum stock.quant quantity on internal locations per variant (single query)."""
        if not variant_ids:
            return {}
        quants = self.env['stock.quant'].sudo().search_read(
            [('product_id', 'in', variant_ids), ('location_id.usage', '=', 'internal')],
            ['product_id', 'quantity'],
        )
        totals = {}
        for quant in quants:
            product = quant['product_id']
            pid = product[0] if isinstance(product, (list, tuple)) else product
            totals[pid] = totals.get(pid, 0.0) + (quant['quantity'] or 0.0)
        return totals
