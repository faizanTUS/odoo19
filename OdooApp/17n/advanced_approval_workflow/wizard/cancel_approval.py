# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CancelApproval(models.TransientModel):
    _name = 'approval.cancel.wizard'
    _description = 'Cancel Approval Wizard'

    reason = fields.Text(string='Cancellation Reason')

    def action_cancel(self):
        self.ensure_one()
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            raise UserError(_('No approval request selected'))
        
        approvals = self.env['multi.approval'].browse(active_ids)
        for approval in approvals:
            if approval.state in ('approved', 'cancel'):
                raise UserError(_('Cannot cancel an already approved or cancelled request'))
            approval.write({'state': 'cancel'})
        
        return {'type': 'ir.actions.act_window_close'}

