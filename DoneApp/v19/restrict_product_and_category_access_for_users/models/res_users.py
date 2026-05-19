# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResUsers(models.Model):
    _inherit = 'res.users'

    restriction_type = fields.Selection([
        ('product', 'Product'),
        ('category', 'Category')
    ], string="Restriction on", default='product', tracking=True)

    allowed_product_ids = fields.Many2many(
        'product.template', string="Allowed Products"
    )

    allowed_category_ids = fields.Many2many(
        'product.category', string="Allowed Categories"
    )

    @api.onchange('restriction_type')
    def _onchange_restriction_type(self):
        """Clear the opposite field when restriction type is changed."""
        if self.restriction_type == 'product' and self.allowed_category_ids:
            self.allowed_category_ids = [(5, 0, 0)]  # Clear categories
            return {
                'warning': {
                    'title': _("Warning"),
                    'message': _("Product category should be removed when you change the Product category to Product."),
                    'type': 'notification',
                }
            }

        if self.restriction_type == 'category' and self.allowed_product_ids:
            self.allowed_product_ids = [(5, 0, 0)]  # Clear products
            return {
                'warning': {
                    'title': _("Warning"),
                    'message': _("Product should be removed when you change the Product to Product category."),
                    'type': 'notification',
                }
            }

    @api.model_create_multi
    def create(self, vals):
        res = super(ResUsers, self).create(vals)
        if 'allowed_product_ids' in vals or 'allowed_category_ids' in vals:
            # self.clear_caches()
            self.env.registry.clear_cache()
        return res

    def write(self, vals):
        if 'restriction_type' in vals:
            if vals['restriction_type'] == 'product' and self.allowed_category_ids:
                raise UserError(_("Product category should be removed when you change the Product category to Product."))

            if vals['restriction_type'] == 'category' and self.allowed_product_ids:
                raise UserError(_("Product should be removed when you change the Product to Product category."))

        res = super(ResUsers, self).write(vals)
        if 'allowed_product_ids' in vals or 'allowed_category_ids' in vals:
            # self.clear_caches()
            self.env.registry.clear_cache()
        return res
