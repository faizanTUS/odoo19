# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SortRecord(models.Model):
    _name = "sorting.record"
    _description = "Sortings for a given record"

    name = fields.Char(string="Name")
    is_active = fields.Boolean(string="Active")
    user_ids = fields.Many2many("res.users", string="User")
    sort_line_ids = fields.One2many("sorting.record.line", "sort_id", string="Sort Line")

    def unlink(self):
        self.sort_line_ids.sudo().unlink()
        return super(SortRecord, self).unlink()

    @api.constrains('sort_line_ids')
    def onchange_sorting_id(self):
        for rec in self.sort_line_ids:
            if self.env['sorting.record.line'].search([('model_id', '=', rec.model_id.id), ('id', '!=', rec.id)]).ids:
                raise ValidationError(_("Only one field per model!!"))


class SortRecordLine(models.Model):
    _name = "sorting.record.line"

    model_id = fields.Many2one("ir.model", string="Model")
    fields_id = fields.Many2one("ir.model.fields", string="Field", domain="[('model_id' ,'=',model_id)]")
    order_type = fields.Selection([('asc', "Ascending"), ('desc', "Descending")], string="Order")
    sort_id = fields.Many2one('sorting.record')


class BaseModel(models.BaseModel):
    _inherit = 'base'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        all_sort_line_id = self.env['sorting.record.line'].sudo().search(
            [('sort_id.is_active', '=', True), ('model_id.model', '=', self._name)])
        if all_sort_line_id:
            return super(BaseModel, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=all_sort_line_id.fields_id.name + ' ' + all_sort_line_id.order_type, **read_kwargs)
        return super(BaseModel, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)


    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        all_sort_line_id = self.env['sorting.record.line'].sudo().search(
            [('sort_id.is_active', '=', True), ('model_id.model', '=', self._name)])
        if all_sort_line_id:
            return self._search(args, order=all_sort_line_id.fields_id.name + ' ' + all_sort_line_id.order_type,limit=limit, access_rights_uid=name_get_uid)
        return super(BaseModel, self)._name_search(args, limit=limit, access_rights_uid=name_get_uid)
