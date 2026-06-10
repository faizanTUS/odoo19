# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MultiApprovalTypeBase(models.Model):
    _name = 'multi.approval.type'
    _description = 'Approval Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    line_ids = fields.One2many('multi.approval.type.line', 'type_id', string='Approval Lines')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)


