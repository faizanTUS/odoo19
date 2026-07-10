# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    hide_pricelist_price = fields.Boolean(
        string='Hide Pricelist Price on Product',
        default=False,
        help='If set, the pricelist price table will not be displayed on this product form.',
    )
    hide_pricelist_ids = fields.Many2many(
        comodel_name='product.pricelist',
        relation='product_template_hide_pricelist_rel',
        column1='product_tmpl_id',
        column2='pricelist_id',
        string='Hide Pricelist From the Product',
        help='Select pricelists that should not be displayed in the pricelist price table on this product.',
    )
    pricelist_price_line_ids = fields.One2many(
        comodel_name='product.pricelist.price.line',
        inverse_name='product_tmpl_id',
        string='Pricelist Price on The Product',
        compute='_compute_pricelist_price_line_ids',
        readonly=True,
    )
    user_display_pricelist_on_product = fields.Boolean(
        string='User: Display Pricelist on Product',
        compute='_compute_user_display_pricelist_on_product',
        help='Technical: mirrors current user preference to show/hide pricelist section in view.',
    )

    @api.depends()
    def _compute_user_display_pricelist_on_product(self):
        for template in self:
            template.user_display_pricelist_on_product = self.env.user.display_pricelist_on_product

    # @api.depends('list_price', 'currency_id', 'hide_pricelist_price', 'hide_pricelist_ids')
    # def _compute_pricelist_price_line_ids(self):
    #     Line = self.env['product.pricelist.price.line']
    #     for template in self:
    #         if template.hide_pricelist_price or not template.id:
    #             template.pricelist_price_line_ids = Line
    #             continue
    #         # Use first variant for price when on template (or template if single variant)
    #         product = template.product_variant_id if template.product_variant_count == 1 else template
    #         template.pricelist_price_line_ids = template._get_pricelist_price_lines(product)
    #
    # def _get_pricelist_price_lines(self, product):
    #     """Build transient lines for pricelist prices for the given product (template or variant)."""
    #     self.ensure_one()
    #     Line = self.env['product.pricelist.price.line']
    #     if self.hide_pricelist_price or not self.id:
    #         return Line
    #     # Remove existing display lines for this product/template to avoid accumulation
    #     if product._name == 'product.product':
    #         Line.search([('product_id', '=', product.id)]).unlink()
    #     else:
    #         Line.search([
    #             ('product_tmpl_id', '=', self.id),
    #             ('product_id', '=', False),
    #         ]).unlink()
    #     # Only pricelists with "Show on Product Form" and not in product's hide list
    #     pricelists = self.env['product.pricelist'].search([
    #         ('active', '=', True),
    #         ('display_on_product_form', '=', True),
    #     ])
    #     pricelists = pricelists - self.hide_pricelist_ids
    #     if not pricelists:
    #         return Line
    #     date = fields.Datetime.now()
    #     quantity = 1.0
    #     lines_vals = []
    #     for pricelist in pricelists:
    #         results = pricelist._compute_price_rule(
    #             product, quantity, date=date, compute_price=True
    #         )
    #         price, rule_id = results.get(product.id, (0.0, False))
    #         rule = self.env['product.pricelist.item'].browse(rule_id) if rule_id else self.env['product.pricelist.item']
    #         vals = {
    #             'product_tmpl_id': self.id,
    #             'product_id': product.id if product._name == 'product.product' else False,
    #             'pricelist_id': pricelist.id,
    #             'min_quantity': rule.min_quantity if rule else 0.0,
    #             'price': price,
    #             'currency_id': pricelist.currency_id.id,
    #             'date_start': rule.date_start if rule else False,
    #             'date_end': rule.date_end if rule else False,
    #         }
    #         lines_vals.append(vals)
    #     if not lines_vals:
    #         return Line
    #     return Line.create(lines_vals)

    @api.depends('list_price', 'currency_id', 'hide_pricelist_price', 'hide_pricelist_ids')
    def _compute_pricelist_price_line_ids(self):
        Line = self.env['product.pricelist.price.line']
        for template in self:
            if template.hide_pricelist_price or not template.id:
                template.pricelist_price_line_ids = Line
                continue
            product = template.product_variant_id if template.product_variant_count == 1 else template
            template.pricelist_price_line_ids = template._get_pricelist_price_lines(product)

    def _get_pricelist_price_lines(self, product):
        self.ensure_one()
        Line = self.env['product.pricelist.price.line']
        if self.hide_pricelist_price or not self.id:
            return Line

        if product._name == 'product.product':
            Line.search([('product_id', '=', product.id)]).unlink()
        else:
            Line.search([
                ('product_tmpl_id', '=', self.id),
                ('product_id', '=', False),
            ]).unlink()

        pricelists = self.env['product.pricelist'].search([
            ('active', '=', True),
            ('display_on_product_form', '=', True),
        ])
        pricelists = pricelists - self.hide_pricelist_ids
        if not pricelists:
            return Line

        date = fields.Datetime.now()
        product_variant = product if product._name == 'product.product' else self.product_variant_id
        lines_vals = []

        for pricelist in pricelists:
            # Mirror Odoo's own priority logic from open_pricelist_rules:
            # 1st: variant-level rule, 2nd: template-level rule, 3rd: category, 4th: global
            matching_rule = None

            # Priority 1 — variant specific (applied_on = '0_product_variant')
            if product_variant:
                matching_rule = pricelist.item_ids.filtered(lambda r: (
                        r.applied_on == '0_product_variant'
                        and r.product_id == product_variant
                        and (not r.date_start or r.date_start <= date)
                        and (not r.date_end or r.date_end >= date)
                ))[:1]

            # Priority 2 — template specific (applied_on = '1_product')
            if not matching_rule:
                matching_rule = pricelist.item_ids.filtered(lambda r: (
                        r.applied_on == '1_product'
                        and r.product_tmpl_id == self
                        and (not r.date_start or r.date_start <= date)
                        and (not r.date_end or r.date_end >= date)
                ))[:1]

            # Priority 3 — category (applied_on = '2_product_category')
            if not matching_rule:
                matching_rule = pricelist.item_ids.filtered(lambda r: (
                        r.applied_on == '2_product_category'
                        and r.categ_id == self.categ_id
                        and (not r.date_start or r.date_start <= date)
                        and (not r.date_end or r.date_end >= date)
                ))[:1]

            # Priority 4 — global (applied_on = '3_global')
            if not matching_rule:
                matching_rule = pricelist.item_ids.filtered(lambda r: (
                        r.applied_on == '3_global'
                        and (not r.date_start or r.date_start <= date)
                        and (not r.date_end or r.date_end >= date)
                ))[:1]

            min_qty = matching_rule.min_quantity if matching_rule else 0.0
            compute_qty = max(min_qty, 1.0)

            results = pricelist._compute_price_rule(
                product, compute_qty, date=date, compute_price=True
            )
            price, rule_id = results.get(product.id, (0.0, False))
            rule = self.env['product.pricelist.item'].browse(rule_id) if rule_id else None

            lines_vals.append({
                'product_tmpl_id': self.id,
                'product_id': product.id if product._name == 'product.product' else False,
                'pricelist_id': pricelist.id,
                'min_quantity': min_qty,
                'price': price,
                'currency_id': pricelist.currency_id.id,
                'date_start': rule.date_start if rule else False,
                'date_end': rule.date_end if rule else False,
            })

        if not lines_vals:
            return Line
        return Line.create(lines_vals)