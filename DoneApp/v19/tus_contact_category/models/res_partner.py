# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, fields, models, _


def _default_contact_category(self):
    """Safe default so installs/upgrades do not break on required field."""
    return self.env.ref("tus_contact_category.contact_category_default", raise_if_not_found=False)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    contact_categ_id = fields.Many2one(
        'contact.category', 'Contact Category',
        change_default=True,
        default=lambda self: self.env.ref(
            'tus_contact_category.contact_category_default',
            raise_if_not_found=False
        ),
        required=True,
        index=True,
        ondelete="restrict",
    )

    @api.onchange('contact_categ_id')
    def _onchange_contact_categ_warning(self):
        default_cat = self.env.ref(
            "tus_contact_category.contact_category_default",
            raise_if_not_found=False
        )
        if default_cat and self.contact_categ_id == default_cat:
            return {
                "warning": {
                    "title": _("Governance Warning"),
                    "message": _(
                        "The 'General' category is a fallback only. "
                        "Please assign a proper Contact Category."
                    ),
                }
            }


    @api.model_create_multi
    def create(self, vals_list):
        """Backstop. Ensures legacy imports don't create partners without a category."""
        default_categ = self.env.ref(
            "tus_contact_category.contact_category_default", raise_if_not_found=False
        )
        if default_categ:
            for vals in vals_list:
                vals.setdefault("contact_categ_id", default_categ.id)
        return super().create(vals_list)
