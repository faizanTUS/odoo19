# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # POS Combo Products (advanced) configuration
    is_combo_product = fields.Boolean(
        string='Is Combo Product',
        help='Enable to sell this product as a combo: customer selects components in POS.',
    )
    max_combo_items = fields.Integer(
        string='Max Combo Items',
        default=0,
        help='Maximum number of distinct combo items the customer can add. 0 = no limit.',
    )
    combo_display = fields.Selection(
        [
            ('list', 'List View'),
            ('grid', 'Grid View'),
        ],
        string='Combo Display',
        default='list',
        help='How to show combo selection in POS popup.',
    )
    pos_combo_group_ids = fields.Many2many(
        'pos.combo.group',
        string='Combo Groups',
        help='Groups of products the customer can choose from for this combo.',
    )
    pos_combo_line_ids = fields.One2many(
        'pos.product.combo.line',
        'product_tmpl_id',
        string='Combo Line',
        help='Direct combo lines (component products with min/max/default qty).',
    )

    @api.constrains('pos_combo_line_ids', 'pos_combo_group_ids')
    def _check_unique_combo_products(self):
        for tmpl in self:
            if not tmpl.is_combo_product:
                continue
            products = set()
            # Check direct lines
            for line in tmpl.pos_combo_line_ids:
                if line.product_id in products:
                    raise ValidationError(
                        _('Duplicate product "%s" found in combo lines.') % line.product_id.display_name)
                products.add(line.product_id)
            # Check groups
            for group in tmpl.pos_combo_group_ids:
                for line in group.line_ids:
                    if line.product_id in products:
                        raise ValidationError(_('Duplicate product "%s" found in combo groups (group: %s).') % (
                            line.product_id.display_name, group.name))
                    products.add(line.product_id)

    @api.onchange('type')
    def _onchange_type_clear_combo(self):
        if self.type != 'combo' and self.env.context.get('clear_combo_from_type'):
            self.is_combo_product = False

    @api.onchange('is_combo_product')
    def _onchange_is_combo_product(self):
        if self.is_combo_product:
            self.detailed_type = 'service'

    @api.constrains('is_combo_product', 'pos_combo_line_ids', 'pos_combo_group_ids', 'type')
    def _check_combo_has_options(self):
        for tmpl in self:
            if not tmpl.is_combo_product:
                continue
            # if tmpl.type != 'service':
            #     raise ValidationError(
            #         _('Combo products must be of type "Service" to avoid inventory tracking on the main product.')
            #     )
            has_lines = tmpl.pos_combo_line_ids
            has_groups = any(g.line_ids for g in tmpl.pos_combo_group_ids)
            if not has_lines and not has_groups:
                raise ValidationError(
                    _('Combo product must have at least one Combo Line or one Combo Group with lines.')
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_combo_product'):
                vals['detailed_type'] = 'service'
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('is_combo_product'):
            vals['detailed_type'] = 'service'
        return super().write(vals)

    def action_set_type_service(self):
        """Helper to force type to service for existing combo products."""
        self.ensure_one()
        self.write({'detailed_type': 'service'})
        return True
