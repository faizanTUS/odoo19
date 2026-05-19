# Part of TechUltra Solutions Pvt Ltd. See COPYRIGHT & LICENSE files for full copyright and licensing details.
import itertools
from odoo import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _prepare_color_size_matrix_data(self, pricelist=None, partner=None):
        """Prepare color-size matrix data for product variants with optimized performance."""
        self.ensure_one()

        attribute_lines = self.valid_product_template_attribute_line_ids
        if not attribute_lines:
            return {}

        # Identify color and size attributes
        color_line = self._find_color_attribute(attribute_lines)
        if not color_line:
            return {}

        other_attributes = attribute_lines.filtered(
            lambda line: line.attribute_id.id != color_line.attribute_id.id
        )
        if not other_attributes:
            return {}

        size_line = self._find_size_attribute(other_attributes)
        if not size_line:
            return {}

        remaining_attributes = other_attributes.filtered(
            lambda line: line.attribute_id.id != size_line.attribute_id.id
        )

        # Get active values
        # color_values = color_line.value_ids.filtered('active')
        color_values = color_line.value_ids
        size_values = size_line.value_ids
        # size_values = size_line.value_ids.filtered('active')
        if not color_values or not size_values:
            return {}

        # Build optimized variant lookup with single iteration
        variant_lookup = self._build_variant_lookup(
            color_line.attribute_id.id,
            size_line.attribute_id.id,
            remaining_attributes
        )

        # Generate column combinations
        column_combinations = self._generate_column_combinations(
            size_values, remaining_attributes
        )

        # Build price context once
        price_ctx = self._build_price_context(pricelist, partner)
        currency = (pricelist.currency_id if pricelist else self.currency_id).sudo()

        # Build matrix rows
        rows = self._build_matrix_rows(
            color_values, column_combinations, variant_lookup, price_ctx
        )

        return {
            'product_template_id': self.id,
            'color_attribute_id': color_line.attribute_id.id,
            'size_attribute_id': size_line.attribute_id.id,
            'column_headers': [
                {'id': idx, 'name': combo['header_name'], 'combo_key': combo['combo_key']}
                for idx, combo in enumerate(column_combinations)
            ],
            'rows': rows,
            'currency': {
                'symbol': currency.symbol,
                'position': currency.position,
                'decimal_places': currency.decimal_places or 2,
            },
        }

    def _find_color_attribute(self, attribute_lines):
        """Find the color attribute line."""
        color_names = {'color', 'colour'}
        return attribute_lines.filtered(
            lambda line: line.attribute_id.display_type == 'color'
                         or (line.attribute_id.name and line.attribute_id.name.strip().lower() in color_names)
        )[:1]

    def _find_size_attribute(self, other_attributes):
        """Find the size attribute line."""
        return other_attributes.filtered(lambda line: line.attribute_id.is_dimension == True)

    def _build_variant_lookup(self, color_attr_id, size_attr_id, remaining_attributes):
        """Build variant lookup dictionary with optimized key generation."""
        variant_lookup = {}
        remaining_attr_ids = [attr.attribute_id.id for attr in remaining_attributes]

        for variant in self.product_variant_ids:
            ptavs = variant.product_template_attribute_value_ids

            # Create attribute mapping for quick lookup
            attr_map = {
                ptav.attribute_id.id: ptav.product_attribute_value_id.id
                for ptav in ptavs
            }

            color_id = attr_map.get(color_attr_id)
            size_id = attr_map.get(size_attr_id)

            if color_id and size_id:
                # Build key with remaining attributes
                key_parts = [color_id, size_id]
                key_parts.extend(attr_map.get(attr_id) for attr_id in remaining_attr_ids)
                variant_lookup[tuple(key_parts)] = variant

        return variant_lookup

    def _generate_column_combinations(self, size_values, remaining_attributes):
        """Generate all combinations of size + additional attributes."""
        column_combinations = []

        if not remaining_attributes:
            # No additional attributes, just size
            return [
                {
                    'size_id': size.id,
                    'size_name': size.display_name,
                    'header_name': size.display_name,
                    'combo_key': (size.id,),
                    'additional_attrs': {},
                }
                for size in size_values
            ]

        # Get all values for remaining attributes
        remaining_attr_values = [
            [
                {'attr_id': attr.attribute_id.id, 'value': val}
                for val in attr.value_ids
                # for val in attr.value_ids.filtered('active')
            ]
            for attr in remaining_attributes
        ]

        # Generate cartesian product of all combinations
        for size in size_values:
            for combo in itertools.product(*remaining_attr_values):
                header_parts = [size.display_name]
                combo_attrs = {}
                combo_ids = []

                for item in combo:
                    header_parts.append(item['value'].display_name)
                    combo_attrs[item['attr_id']] = item['value'].id
                    combo_ids.append(item['value'].id)

                column_combinations.append({
                    'size_id': size.id,
                    'size_name': size.display_name,
                    'header_name': ' / '.join(header_parts),
                    'combo_key': (size.id,) + tuple(combo_ids),
                    'additional_attrs': combo_attrs,
                })

        return column_combinations

    def _build_price_context(self, pricelist, partner):
        """Build price context dictionary."""
        context = {}
        if pricelist:
            context['pricelist'] = pricelist.id
        if partner:
            context['partner_id'] = partner.id
        context['quantity'] = 1
        return context

    def _build_matrix_rows(self, color_values, column_combinations, variant_lookup, price_ctx):
        """Build matrix rows with variant data."""
        rows = []

        for color in color_values:
            entries = []

            for col_combo in column_combinations:
                # Build lookup key
                lookup_key = (color.id,) + col_combo['combo_key']
                variant = variant_lookup.get(lookup_key)

                # Calculate price if variant exists
                unit_price = 0.0
                if variant and price_ctx:
                    variant_with_ctx = variant.with_context(**price_ctx)
                    unit_price = variant_with_ctx.lst_price or 0.0

                entries.append({
                    'combo_key': col_combo['combo_key'],
                    'header_name': col_combo['header_name'],
                    'size_id': col_combo['size_id'],
                    'variant_id': variant.id if variant else False,
                    'can_add_to_cart': bool(variant and variant._is_add_to_cart_allowed()),
                    'stock_message': (
                        variant.website_availability
                        if variant and hasattr(variant, 'website_availability')
                        else ''
                    ),
                    'unit_price': unit_price,
                })

            rows.append({
                'color_id': color.id,
                'color_name': color.display_name,
                'html_color': color.html_color,
                'entries': entries,
            })

        return rows

