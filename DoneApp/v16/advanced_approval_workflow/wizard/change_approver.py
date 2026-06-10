# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ChangeApprover(models.TransientModel):
    _name = 'approval.change.approver.wizard'
    _description = 'Change Approver Wizard'

    line_id = fields.Many2one('multi.approval.line', required=True, string='Approval Line')
    new_user_id = fields.Many2one('res.users', required=True, string='New Approver')

    def action_change_approver(self):
        self.ensure_one()
        if not self.env.user.has_group('advanced_approval_workflow.group_approval_manager'):
            raise UserError(_('Only approval managers can change approvers'))
        
        self.line_id.write({'user_id': self.new_user_id.id})
        return {'type': 'ir.actions.act_window_close'}

