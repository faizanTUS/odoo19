# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields

class MultiApprovalTypeLine(models.Model):
    _name = 'multi.approval.type.line'
    _description = 'Approval Type Line'
    _order = 'sequence'

    type_id = fields.Many2one('multi.approval.type')
    name = fields.Char()
    user_id = fields.Many2one('res.users')
    sequence = fields.Integer()
    require_opt = fields.Selection([('Required','Required'),('Optional','Optional')])

    def get_user(self):
        return self.user_id.id
