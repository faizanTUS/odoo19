# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

class MultiApprovalLine(models.Model):
    _name = 'multi.approval.line'
    _description = 'Approval Line'
    _order = 'sequence'

    approval_id = fields.Many2one('multi.approval')
    name = fields.Char()
    user_id = fields.Many2one('res.users')
    sequence = fields.Integer()
    require_opt = fields.Selection([('Required','Required'),('Optional','Optional')])
    state = fields.Selection([
        ('draft','Draft'),
        ('waiting','Waiting'),
        ('approved','Approved'),
        ('refused','Refused')
    ], default='draft')
    refused_reason = fields.Text()