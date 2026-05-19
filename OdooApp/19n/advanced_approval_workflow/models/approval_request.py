# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MultiApproval(models.Model):
    _name = 'multi.approval'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Approval Request'

    code = fields.Char(default='New')
    name = fields.Char(required=True)
    user_id = fields.Many2one('res.users', default=lambda s: s.env.uid)
    type_id = fields.Many2one('multi.approval.type', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancelled')
    ], default='draft', tracking=True)

    line_ids = fields.One2many('multi.approval.line', 'approval_id')
    line_id = fields.Many2one('multi.approval.line')
    complete_date = fields.Datetime()
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

    @api.model
    def create(self, vals):
        # if vals.get('code', 'New') == 'New':
        #     vals['code'] = self.env['ir.sequence'].next_by_code('multi.approval') or 'New'

        for val in vals:
            sequence = self.env['ir.sequence'].next_by_code('multi.approval')
            val['code'] = sequence or 'New'
        return super().create(vals)

    def action_submit(self):
        for rec in self:
            if not rec.type_id.line_ids:
                raise UserError(_('No approvers configured'))
            rec.state = 'submitted'
            rec._create_lines()

    def _create_lines(self):
        for rec in self:
            lines = rec.type_id.line_ids.sorted('sequence')
            for idx, l in enumerate(lines):
                vals = {
                    'approval_id': rec.id,
                    'name': l.name,
                    'user_id': l.get_user(),
                    'sequence': l.sequence,
                    'require_opt': l.require_opt,
                    'state': 'waiting' if idx == 0 else 'draft'
                }
                line = self.env['multi.approval.line'].create(vals)
                if idx == 0:
                    rec.line_id = line

    def action_approve(self):
        self.ensure_one()

        if self.line_id.user_id != self.env.user and not self.env.user.has_group('base.group_system'):
            raise UserError(_('Not authorized'))

        self.line_id.state = 'approved'

        next_line = self.line_ids.filtered(
            lambda l: l.state == 'draft'
        ).sorted('sequence')[:1]

        if next_line:
            next_line.state = 'waiting'
            self.line_id = next_line
        else:
            self.state = 'approved'
            self.complete_date = fields.Datetime.now()

            if self.origin_ref:
                self.origin_ref.with_context(approval_bypass=True).write({
                    'x_review_result': 'approved',
                    'x_need_approval': False
                })
                self.type_id.sudo().run(self.origin_ref)

    def action_refuse(self, reason=''):
        self.ensure_one()
        self.line_id.write({'state': 'refused', 'refused_reason': reason})
        self.state = 'refused'
