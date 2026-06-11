# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ContactCategory(models.Model):
    _name = "contact.category"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Contact Category"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    active = fields.Boolean(default=True)

    name = fields.Char('Name', index='trigram', required=True)
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name', recursive=True,
        store=True)
    parent_id = fields.Many2one('contact.category', 'Parent Category', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True)
    child_id = fields.One2many('contact.category', 'parent_id', 'Child Categories')
    contact_count = fields.Integer(
        string="# Contacts",
        compute="_compute_contact_count",
        help="Number of contacts in this category including its children.",
    )

    @api.ondelete(at_uninstall=False)
    def _unlink_block(self):
        raise UserError(
            _("Contact Categories cannot be deleted. Archive them instead.")
        )

    def write(self, vals):
        default_cat = self.env.ref(
            "tus_contact_category.contact_category_default", raise_if_not_found=False
        )
        if default_cat and default_cat in self:
            forbidden = {"name", "parent_id", "active"}
            if forbidden.intersection(vals):
                raise UserError(
                    _("The default 'General' category cannot be modified.")
                )
        return super().write(vals)

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

    def _compute_contact_count(self):
        """Odoo 18 safe implementation (read_group returns dict rows)."""
        if not self:
            return

        rows = self.env["res.partner"].read_group(
            [("contact_categ_id", "child_of", self.ids)],
            ["contact_categ_id"],
            ["contact_categ_id"],
        )
        # rows: [{'contact_categ_id': (id, name), 'contact_categ_id_count': N}, ...]
        direct_counts = {
            row["contact_categ_id"][0]: row.get("contact_categ_id_count", 0)
            for row in rows
            if row.get("contact_categ_id")
        }

        for categ in self:
            descendants = self.search([("id", "child_of", categ.id)]).ids
            categ.contact_count = sum(direct_counts.get(cid, 0) for cid in descendants)

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive categories.'))

    @api.model
    def name_create(self, name):
        category = self.create({'name': name})
        return category.id, category.display_name

    @api.depends_context('hierarchical_naming')
    def _compute_display_name(self):
        if self.env.context.get('hierarchical_naming', True):
            return super()._compute_display_name()
        for record in self:
            record.display_name = record.name

    @api.ondelete(at_uninstall=False)
    def _unlink_except_default_category(self):
        main_category = self.env.ref('tus_contact_category.contact_category_default', raise_if_not_found=False)
        if main_category and main_category in self:
            raise UserError(_('You cannot delete this contact category, it is the default generic category.'))
