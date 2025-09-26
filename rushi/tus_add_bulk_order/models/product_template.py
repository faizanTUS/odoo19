# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger("Add Bulk Order")


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
                        f"The Product with this Model - {record.model_name} already exist. \n please enter new Model Name.")

    @api.model
    def get_all_variants_info(self, template_id):
        """
        Get all product variants for a given product template,
        including their attributes, stock, and pricing.
        """
        template = self.browse(template_id)
        variants_info = []

        for variant in template.product_variant_ids:
            attributes_display = []
            for ptav in variant.product_template_attribute_value_ids:
                attributes_display.append(f"{ptav.attribute_id.name}: {ptav.product_attribute_value_id.name}")

            qty_available = self._get_variant_stock_quantity(variant.id)

            variants_info.append({
                'variant_id': variant.id,
                'display_name': variant.display_name,
                'attributes_display': ", ".join(attributes_display),
                'qty_available': qty_available,
                'list_price': variant.list_price,
                'wsp_price': variant.list_price  # Using list_price as fallback for wsp_price
            })

        return {
            "image_128": template.image_128,
            "product_name": template.name,
            "variants": variants_info
        }

    def _get_variant_stock_quantity(self, variant_id):
        """Calculate stock quantity for a variant"""
        stock_quants = self.env['stock.quant'].sudo().search([
            ('product_id', '=', variant_id), ('location_id.usage', '=', 'internal')
        ])

        return sum(stock_quants.mapped('quantity'))
