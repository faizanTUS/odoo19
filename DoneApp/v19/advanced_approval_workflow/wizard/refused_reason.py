# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields
class RefusedReason(models.TransientModel):
    _name = 'approval.refused.reason'

    reason = fields.Text(required=True)

    def action_apply(self):
        return self.env['multi.approval'].browse(
            self.env.context['active_ids']
        ).action_refuse(self.reason)
