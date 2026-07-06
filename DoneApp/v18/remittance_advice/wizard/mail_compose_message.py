# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, models


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def default_get(self, fields_list):
        result = super().default_get(fields_list)

        # When opening "Send receipt by email" from a Vendor Payment with Remittance Advice
        # enabled, use the Remittance Advice template (and its PDF attachment) instead of
        # the standard payment receipt template.
        active_model = self.env.context.get('active_model')
        if active_model != 'account.payment':
            return result

        active_id = self.env.context.get('active_id')
        active_ids = self.env.context.get('active_ids') or ([active_id] if active_id else [])
        if not active_ids:
            return result

        payments = self.env['account.payment'].browse(active_ids).exists()
        if not payments:
            return result

        # Use remittance template if we're in receipt-by-email flow and at least one
        # vendor payment has remittance_advice enabled (single: that one; multi: first with remittance)
        use_remittance = False
        template_to_use = None
        for payment in payments:
            if payment.partner_type == 'supplier' and payment.remittance_advice:
                use_remittance = True
                template_to_use = payment._get_remittance_advice_template()
                if template_to_use:
                    break

        if use_remittance and template_to_use and 'template_id' in result:
            result['template_id'] = template_to_use.id

        return result
