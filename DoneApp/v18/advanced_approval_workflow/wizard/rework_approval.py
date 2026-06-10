# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ReworkApproval(models.TransientModel):
    _name = 'approval.rework.wizard'
    _description = 'Rework Approval Wizard'

    reason = fields.Text(string='Rework Reason', required=True)

    def action_rework(self):
        self.ensure_one()
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            raise UserError(_('No approval request selected'))
        
        approvals = self.env['multi.approval'].browse(active_ids)
        for approval in approvals:
            if approval.state != 'refused':
                raise UserError(_('Only refused requests can be reworked'))
            approval.write({
                'state': 'draft',
                'line_ids': [(5, 0, 0)],
            })
            approval.line_id = False
        
        return {'type': 'ir.actions.act_window_close'}

