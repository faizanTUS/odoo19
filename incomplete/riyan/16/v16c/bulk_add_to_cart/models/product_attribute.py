# Part of TechUltra Solutions Pvt Ltd. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import _,models, fields,api
from odoo.exceptions import ValidationError

class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    is_dimension = fields.Boolean(string='Size', default=False)

    @api.constrains('is_dimension')
    def _check_only_one_dimension(self):
        for rec in self:
            if rec.is_dimension:
                existing = self.search([
                    ('is_dimension', '=', True),
                    ('id', '!=', rec.id)
                ], limit=1)
                if existing:
                    raise ValidationError(_(
                        "Only one attribute can be marked as a Size (Dimension).\n"
                        f"Already configured on: {existing.name}."
                    ))