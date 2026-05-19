# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

class BaseModel(models.AbstractModel):
    _inherit = 'base'

    def write(self, vals):

        if self._name.startswith('multi.approval'):
            return super().write(vals)

        if self.env.context.get('approval_bypass'):
            return super().write(vals)

        ApprovalType = self.env['multi.approval.type'].sudo()

        for rec in self:

            if not hasattr(rec, 'x_need_approval'):
                continue

            if getattr(rec, 'x_review_result', False) == 'approved':
                continue

            approval_types = ApprovalType.search([
                ('apply_for_model', '=', True),
                ('model_id.model', '=', rec._name),
                ('active', '=', True),
            ])

            for atype in approval_types:
                domain = safe_eval(atype.domain or "[]")

                if rec.filtered_domain(domain):
                    if not getattr(rec, 'x_review_result', False):

                        super(
                            BaseModel,
                            rec.with_context(approval_bypass=True)
                        ).write({
                            'x_need_approval': True,
                            'x_review_result': False,
                        })

                        raise UserError(
                            _("This document requires approval before modification.")
                        )

        return super().write(vals)