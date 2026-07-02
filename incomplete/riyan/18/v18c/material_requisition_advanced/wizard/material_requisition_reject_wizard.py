# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class MaterialRequisitionRejectWizard(models.TransientModel):
    _name = 'material.requisition.reject.wizard'
    _description = 'Reject Material Requisition'

    requisition_id = fields.Many2one(
        'material.requisition',
        string='Material Requisition',
        required=True,
        ondelete='cascade',
    )
    rejection_reason = fields.Text(string='Rejection Reason')
    rejected_by = fields.Char(string='Rejected by role', default=lambda self: self.env.context.get('default_rejected_by', ''))

    def action_reject(self):
        self.ensure_one()
        req = self.requisition_id
        req.write({
            'state': 'rejected',
            'rejected_by_id': self.env.user.id,
            'rejected_date': fields.Datetime.now(),
            'rejection_reason': self.rejection_reason or _('Rejected by %s') % self.rejected_by,
        })
        return {'type': 'ir.actions.act_window_close'}
