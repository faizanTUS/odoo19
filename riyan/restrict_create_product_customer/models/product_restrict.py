# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models,api, _
from odoo.exceptions import AccessError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.user.has_group('restrict_create_product_customer.group_product_create'):
            raise AccessError(_("You do not have permission to create products."))
        return super(ProductTemplate, self).create(vals_list)
