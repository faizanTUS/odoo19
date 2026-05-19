# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    allowed_product_attribute_ids = fields.Many2many(
        comodel_name="product.attribute",
        relation="res_users_product_attribute_restriction_rel",
        column1="user_id",
        column2="attribute_id",
        string="Allowed Product Attributes",
        help=(
            "When the user does not have 'Manage Product Attributes' rights, "
            "only these attributes can be added to products. Leave empty to "
            "allow no attributes (restriction error when adding any attribute)."
        ),
    )
