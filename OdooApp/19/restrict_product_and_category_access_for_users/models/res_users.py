# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResUsers(models.Model):
    _inherit = 'res.users'

    restriction_type = fields.Selection(
        [('product', 'Product'), ('category', 'Category')],
        string="Restriction on",
        default='product',
        tracking=True,
    )

    allowed_product_ids = fields.Many2many(
        'product.template',
        string="Allowed Products",
    )

    allowed_category_ids = fields.Many2many(
        'product.category',
        string="Allowed Categories",
    )

    def _invalidate_access_rules_cache(self):
        self.env.registry.clear_cache()

    def _get_restricted_product_template_ids(self):
        """Templates a restricted user may read (configured allow-list + SO lines)."""
        self.ensure_one()
        template_ids = set()
        if self.restriction_type == 'category':
            if self.allowed_category_ids:
                templates = self.env['product.template'].search([
                    '|',
                    ('categ_id', 'in', self.allowed_category_ids.ids),
                    ('categ_id', 'child_of', self.allowed_category_ids.ids),
                ])
                template_ids.update(templates.ids)
        else:
            template_ids.update(self.allowed_product_ids.ids)
        template_ids.update(self._get_sale_order_product_template_ids())
        return list(template_ids)

    def _get_sale_order_product_template_ids(self):
        """Templates used on sale orders the current user can access."""
        if 'sale.order' not in self.env:
            return []
        orders = self.env['sale.order'].search([])
        if not orders:
            return []
        lines = self.env['sale.order.line'].search([
            ('order_id', 'in', orders.ids),
            ('product_id', '!=', False),
        ])
        return lines.product_id.product_tmpl_id.ids

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        if any(
            key in vals
            for vals in vals_list
            for key in ('allowed_product_ids', 'allowed_category_ids', 'groups_id')
        ):
            users._invalidate_access_rules_cache()
        return users

    def write(self, vals):
        if 'restriction_type' in vals:
            if vals['restriction_type'] == 'product' and self.allowed_category_ids:
                raise UserError(
                    _(
                        "Product category should be removed when you change the Product category to Product."
                    )
                )

            if vals['restriction_type'] == 'category' and self.allowed_product_ids:
                raise UserError(
                    _("Product should be removed when you change the Product to Product category.")
                )

        res = super().write(vals)
        if any(
            key in vals
            for key in ('allowed_product_ids', 'allowed_category_ids', 'groups_id')
        ):
            self._invalidate_access_rules_cache()
        return res

    @api.onchange('restriction_type')
    def _onchange_restriction_type(self):
        if self.restriction_type == 'product' and self.allowed_category_ids:
            self.allowed_category_ids = [(5, 0, 0)]
            return {
                'warning': {
                    'title': _("Warning"),
                    'message': _(
                        "Product category should be removed when you change the Product category to Product."
                    ),
                    'type': 'notification',
                }
            }

        if self.restriction_type == 'category' and self.allowed_product_ids:
            self.allowed_product_ids = [(5, 0, 0)]
            return {
                'warning': {
                    'title': _("Warning"),
                    'message': _(
                        "Product should be removed when you change the Product to Product category."
                    ),
                    'type': 'notification',
                }
            }
