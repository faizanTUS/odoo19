# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ProductTemplateAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"

    def _check_product_attribute_restriction(self, attribute):
        """Raise UserError if the current user is not allowed to use this attribute."""
        if not attribute:
            return
        user = self.env.user
        has_group = user.has_group("product_attribute_restriction.group_product_attribute_manager")
        allowed = user.allowed_product_attribute_ids
        _logger.info(
            "[User Based Product Attribute Restrictions | Advanced Product Attribute Security] user=%s (id=%s) attribute=%s (id=%s) "
            "has_manage_group=%s allowed_count=%s allowed_ids=%s",
            user.login, user.id, attribute.display_name, attribute.id,
            has_group, len(allowed), allowed.ids,
        )
        if has_group:
            _logger.info("[User Based Product Attribute Restrictions | Advanced Product Attribute Security] ALLOWED (user has Manage Product Attributes)")
            return
        if attribute in allowed:
            _logger.info("[User Based Product Attribute Restrictions | Advanced Product Attribute Security] ALLOWED (attribute in user allowed list)")
            return
        _logger.warning(
            "[User Based Product Attribute Restrictions | Advanced Product Attribute Security] DENIED for user=%s attribute=%s",
            user.login, attribute.display_name,
        )
        raise UserError(
            _(
                "Product Attribute restriction: You are not allowed to add the attribute '%(attribute)s' to products. "
                "Contact your administrator to get 'Manage Product Attributes' rights or to add this attribute to your allowed list.",
                attribute=attribute.display_name,
            )
        )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            attribute_id = vals.get("attribute_id")
            if attribute_id:
                attribute = self.env["product.attribute"].browse(attribute_id).exists()
                self._check_product_attribute_restriction(attribute)
        return super().create(vals_list)

    def write(self, values):
        if "attribute_id" in values:
            attribute = self.env["product.attribute"].browse(values["attribute_id"]).exists()
            self._check_product_attribute_restriction(attribute)
        elif values.get("active", True):
            # Reactivation or other write: ensure user can use the line's attribute
            for line in self:
                if line.attribute_id:
                    self._check_product_attribute_restriction(line.attribute_id)
        return super().write(values)
