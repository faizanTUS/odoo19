# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ProductTemplateAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"

    def _check_product_attribute_restrictions(self, attributes):
        """Raise UserError if the current user is not allowed to use one or more attributes."""
        if not attributes:
            return
        attributes = attributes.exists()
        if not attributes:
            return
        user = self.env.user
        has_group = user.has_group("product_attribute_restriction.group_product_attribute_manager")
        allowed = user.allowed_product_attribute_ids
        _logger.info(
            "[User Based Product Attribute Restrictions | Advanced Product Attribute Security] user=%s (id=%s) attributes=%s "
            "has_manage_group=%s allowed_count=%s allowed_ids=%s",
            user.login, user.id, attributes.ids,
            has_group, len(allowed), allowed.ids,
        )
        if has_group:
            _logger.info("[User Based Product Attribute Restrictions | Advanced Product Attribute Security] ALLOWED (user has Manage Product Attributes)")
            return
        restricted_attributes = attributes - allowed
        if not restricted_attributes:
            _logger.info("[User Based Product Attribute Restrictions | Advanced Product Attribute Security] ALLOWED (all attributes in user allowed list)")
            return
        restricted_names = ", ".join(f"'{name}'" for name in restricted_attributes.mapped("display_name"))
        _logger.warning(
            "[User Based Product Attribute Restrictions | Advanced Product Attribute Security] DENIED for user=%s attributes=%s",
            user.login, restricted_attributes.ids,
        )
        raise UserError(
            _(
                "Product Attribute restriction: You are not allowed to add these attributes to products: [%(attributes)s]. "
                "Contact your administrator to get 'Manage Product Attributes' rights or to add these attributes to your allowed list.",
                attributes=restricted_names,
            )
        )

    @api.model_create_multi
    def create(self, vals_list):
        attribute_ids = {vals.get("attribute_id") for vals in vals_list if vals.get("attribute_id")}
        if attribute_ids:
            attributes = self.env["product.attribute"].browse(list(attribute_ids))
            self._check_product_attribute_restrictions(attributes)
        return super().create(vals_list)

    def write(self, values):
        if "attribute_id" in values:
            attribute = self.env["product.attribute"].browse(values["attribute_id"]).exists()
            self._check_product_attribute_restrictions(attribute)
        elif values.get("active", True):
            # Reactivation or other write: ensure user can use the line's attribute
            attributes = self.mapped("attribute_id")
            self._check_product_attribute_restrictions(attributes)
        return super().write(values)
