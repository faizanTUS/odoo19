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
        self.env.registry.clear_caches()

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

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        if any(
            'allowed_product_ids' in vals or 'allowed_category_ids' in vals
            for vals in vals_list
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
        if 'allowed_product_ids' in vals or 'allowed_category_ids' in vals:
            self._invalidate_access_rules_cache()
        return res
