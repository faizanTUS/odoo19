# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class RequestApproval(models.TransientModel):
    _name = 'approval.request.wizard'
    _description = 'Request Approval Wizard'

    type_id = fields.Many2one('multi.approval.type', required=True, string='Approval Type')
    name = fields.Char(required=True, string='Request Name')
    origin_ref = fields.Reference(
        selection='_selection_origin_ref',
        string='Source Document'
    )

    @api.model
    def _selection_origin_ref(self):
        """Return available models for approval"""
        # Use sudo() to bypass access rights for ir.model
        models = self.env['ir.model'].sudo().search([
            ('model', 'in', ['product.product', 'product.template', 'sale.order', 'purchase.order'])
        ])
        return [(model.model, model.name) for model in models]

    def action_request_approval(self):
        self.ensure_one()
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        
        if not active_model or not active_id:
            raise UserError(_('No record selected'))
        
        record = self.env[active_model].browse(active_id)
        
        # Create approval request
        origin_ref = f'{active_model},{active_id}' if active_model and active_id else False
        approval = self.env['multi.approval'].create({
            'name': self.name,
            'type_id': self.type_id.id,
            'origin_ref': origin_ref,
        })
        
        # Mark record as needing approval
        if hasattr(record, 'x_need_approval'):
            record.write({'x_need_approval': True})
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Approval Request'),
            'res_model': 'multi.approval',
            'res_id': approval.id,
            'view_mode': 'form',
            'target': 'current',
        }

