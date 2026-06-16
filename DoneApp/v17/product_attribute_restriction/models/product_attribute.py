# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    def _check_manage_product_attributes(self):
        """Raise UserError if the current user cannot create/edit attributes (master data)."""
        if self.env.su:
            return
        if self.env.user.has_group("product_attribute_restriction.group_product_attribute_manager"):
            return
        _logger.warning(
            "[User Based Product Attribute Restrictions | Advanced Product Attribute Security] DENIED create/write attribute for user=%s",
            self.env.user.login,
        )
        raise UserError(
            _(
                "You are not allowed to create or edit Product Attributes. "
                "Contact your administrator to get 'Manage Product Attributes' rights."
            )
        )

    @api.model_create_multi
    def create(self, vals_list):
        self._check_manage_product_attributes()
        return super().create(vals_list)

    def write(self, vals):
        self._check_manage_product_attributes()
        return super().write(vals)

    def unlink(self):
        self._check_manage_product_attributes()
        return super().unlink()
