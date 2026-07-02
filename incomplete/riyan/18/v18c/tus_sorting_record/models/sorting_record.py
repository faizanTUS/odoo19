# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

import logging

_logger = logging.getLogger(__name__)

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

# class BaseModelI(models.AbstractModel):
#     _inherit = 'base'


class BaseModel(models.BaseModel):
    _inherit = 'base'

    @api.model
    def web_search_read(self, domain, specification, offset=0, limit=None, order=None, count_limit=None):
        records = self.search_fetch(domain, specification.keys(), offset=offset, limit=limit, order=order)
        all_sort_line_id = self.env['sorting.record.line'].sudo().search(
            [('sort_id.is_active', '=', True), ('model_id.model', '=', records._name)])
        if all_sort_line_id:
            order= all_sort_line_id.fields_id.name + ' ' + all_sort_line_id.order_type
            return super(BaseModel, self).web_search_read(domain=domain, specification=specification, offset=offset,limit=limit,order=order,count_limit=count_limit)
        return super(BaseModel, self).web_search_read(domain=domain, specification=specification, offset=offset,limit=limit,order=order, count_limit=count_limit)

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = list(domain or ())
        search_fnames = self._rec_names_search or ([self._rec_name] if self._rec_name else [])
        if not search_fnames:
            _logger.warning("Cannot execute name_search, no _rec_name or _rec_names_search defined on %s", self._name)
        # optimize out the default criterion of ``like ''`` that matches everything
        elif not (name == '' and operator in ('like', 'ilike')):
            aggregator = expression.AND if operator in expression.NEGATIVE_TERM_OPERATORS else expression.OR
            domain += aggregator([[(field_name, operator, name)] for field_name in search_fnames])
        all_sort_line_id = self.env['sorting.record.line'].sudo().search([('sort_id.is_active', '=', True), ('model_id.model', '=', self._name)])
        if all_sort_line_id:
            return self._search(domain, limit=limit, order=all_sort_line_id.fields_id.name + ' ' + all_sort_line_id.order_type)
        return super(BaseModel, self)._search(domain, limit=limit, order=order)


