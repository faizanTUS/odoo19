# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api

class MultiApprovalType(models.Model):
    _inherit = 'multi.approval.type'

    apply_for_model = fields.Boolean(
        string="Apply for Model",
        help="Enable approval rules for a specific model"
    )
    model_id = fields.Many2one(
        'ir.model',
        string="Target Model",
        ondelete='cascade',
        domain=[('model', 'in', ['product.product', 'product.template', 'sale.order', 'purchase.order', 'account.move', 'stock.picking'])],
        help="Select the model that requires approval"
    )
    domain = fields.Text(
        string="Activation Domain",
        default="[]",
        help="Domain that triggers approval requirement"
    )

    def _create_technical_fields(self):
        IrField = self.env['ir.model.fields'].sudo()

        model_rec = self.model_id
        if not model_rec:
            return

        field_defs = {
            'x_need_approval': 'boolean',
            'x_has_request_approval': 'boolean',
            'x_review_result': 'char',
        }

        for name, ttype in field_defs.items():
            if not IrField.search([
                ('model_id', '=', model_rec.id),
                ('name', '=', name)
            ], limit=1):
                IrField.create({
                    'name': name,
                    'model_id': model_rec.id,
                    'model': model_rec.model,
                    'ttype': ttype,
                    'store': True,
                    'copied': False,
                    'readonly': True,
                })

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        if rec.apply_for_model and rec.model_id:
            rec._create_technical_fields()
        return rec

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.apply_for_model and rec.model_id:
                rec._create_technical_fields()
        return res

    def run(self, record):
        """Execute action after approval is complete"""
        if record and hasattr(record, 'x_review_result'):
            record.with_context(approval_bypass=True).write({
                'x_review_result': 'approved',
                'x_need_approval': False
            })
        return True
