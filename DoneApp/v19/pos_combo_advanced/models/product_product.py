# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Related fields from template
    is_combo_product = fields.Boolean(
        related='product_tmpl_id.is_combo_product',
        readonly=True,
        store=False
    )
    max_combo_items = fields.Integer(
        related='product_tmpl_id.max_combo_items',
        readonly=True,
        store=False
    )
    combo_display = fields.Selection(
        related='product_tmpl_id.combo_display',
        readonly=True,
        store=False
    )

    # CRITICAL: Computed field that will be loaded automatically by POS
    pos_combo_options = fields.Json(
        string='POS Combo Options',
        compute='_compute_pos_combo_options',
        store=False,
    )

    @api.depends('is_combo_product', 'product_tmpl_id.pos_combo_line_ids', 'product_tmpl_id.pos_combo_group_ids')
    def _compute_pos_combo_options(self):
        """
        Compute combo options so they're automatically available in POS.
        This gets called automatically when POS loads product data.
        """
        for product in self:
            options = self._get_pos_combo_options_for_product(product)
            product.pos_combo_options = options

    def _get_pos_combo_options_for_product(self, product):
        """
        Helper method to get combo options for a single product.
        Separated from _compute to make it easier to test.
        """
        if not product.is_combo_product:
            return []

        tmpl = product.product_tmpl_id
        options = []

        # Direct lines from product template
        for line in tmpl.pos_combo_line_ids:
            options.append({
                'product_id': line.product_id.id,
                'min_qty': line.min_qty,
                'max_qty': line.max_qty,
                'default_qty': line.default_qty,
                'group_name': False,
            })

        # Lines from combo groups
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

    @api.model
    def _load_pos_data_fields(self, config_id):
        """
        PURPOSE: Tell POS which fields to load when fetching product data.

        This method returns a list of field names that POS should request
        when loading products. By adding 'pos_combo_options' here, we tell
        POS to include this field in the search_read() call.

        When search_read() encounters a computed field, Odoo automatically
        calls the compute method (_compute_pos_combo_options) and includes
        the computed value in the response.
        """
        # Get the base fields from parent class
        fields_list = super()._load_pos_data_fields(config_id)

        # Add our custom fields
        extra_fields = [
            'is_combo_product',  # Boolean - is this a combo?
            'max_combo_items',  # Integer - max items allowed
            'combo_display',  # Selection - list or grid view
            'pos_combo_options',  # Json - THE COMBO OPTIONS DATA
        ]

        # Ensure fields_list is a list
        if not isinstance(fields_list, list):
            fields_list = list(fields_list)

        # Add each field if not already present
        for field_name in extra_fields:
            if field_name not in fields_list:
                fields_list.append(field_name)

        return fields_list

    @api.model
    def _load_pos_data_domain(self, data, config):
        """
        PURPOSE: Tell POS which products to load (filtering).

        This method returns a domain (filter) that determines which products
        should be loaded in POS. We can modify it to ensure combo products
        are always included.

        In Odoo 19, this method takes 3 parameters: self, data, config
        """
        return super()._load_pos_data_domain(data, config)