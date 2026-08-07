from odoo import models, fields, _


class RmaRejectWizard(models.TransientModel):
    _name = 'rma.reject.wizard'
    _description = 'RMA Reject Wizard'

    rma_id = fields.Many2one('customer.rma', string='Customer RMA')
    srma_id = fields.Many2one('supplier.rma', string='Supplier RMA')
    model_name = fields.Char(string='Target Model', default='customer.rma')
    reject_reason = fields.Text(string='Reason for Rejection', required=True)

    def action_reject_confirm(self):
        self.ensure_one()
        if self.model_name == 'supplier.rma' and self.srma_id:
            self.srma_id.write({
                'state': 'rejected',
                'reject_reason': self.reject_reason,
            })
            return
        if self.rma_id:
            self.rma_id.write({
                'state': 'rejected',
                'reject_reason': self.reject_reason,
            })
            template = self.env.ref(
                'rma_management.email_template_rma_rejected', raise_if_not_found=False,
            )
            if template:
                template.send_mail(self.rma_id.id, force_send=False)
