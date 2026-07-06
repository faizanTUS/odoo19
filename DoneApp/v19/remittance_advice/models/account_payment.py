# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
import base64
from odoo import api, fields, models
from odoo.tools.misc import formatLang, format_date


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    remittance_advice = fields.Boolean(
        string='Remittance Advice',
        default=False,
        help='When enabled, the "Send receipt by email" action will use the Remittance Advice email template '
             'and attach the Remittance Advice PDF. Only applicable for Vendor Payments.',
    )
    remittance_advice_template_id = fields.Many2one(
        comodel_name='mail.template',
        string='Remittance Advice Email Template',
        domain="[('model', '=', 'account.payment')]",
        help='Email template to use when sending Remittance Advice by email. '
             'If not set, the default Remittance Advice (Vendor Payments) template is used.',
    )

    @api.onchange('partner_type')
    def _onchange_partner_type_remittance_advice(self):
        """Reset Remittance Advice for non-vendor payments."""
        if self.partner_type != 'supplier':
            self.remittance_advice = False
            self.remittance_advice_template_id = False

    def _get_remittance_advice_template(self):
        """Return the mail template to use for remittance advice email."""
        self.ensure_one()
        if self.remittance_advice_template_id:
            return self.remittance_advice_template_id
        return self.env.ref(
            'remittance_advice.mail_template_remittance_advice',
            raise_if_not_found=False,
        )

    def _format_address(self, partner):
        """Format partner address as multi-line string."""
        if not partner:
            return ''
        parts = []
        if partner.street:
            parts.append(partner.street)
        if partner.street2:
            parts.append(partner.street2)
        city_zip = []
        if partner.city:
            city_zip.append(partner.city)
        if partner.state_id:
            city_zip.append(partner.state_id.name)
        if partner.zip:
            city_zip.append(partner.zip)
        if city_zip:
            parts.append(' '.join(city_zip))
        if partner.country_id:
            parts.append(partner.country_id.name)
        return '\n'.join(parts) if parts else ''

    def _get_remittance_advice_report_values(self):
        """Values for the Remittance Advice report (1st image layout): recipient, company, payment summary, bill table, signature."""
        self.ensure_one()
        company = self.company_id
        partner = self.partner_id
        company_partner = company.partner_id

        # Company signature (always base64 str for template; ensure full content with bin_size=False)
        signature_b64 = None
        company_with_bin = company.with_context(bin_size=False)
        if hasattr(company_with_bin, 'company_signature') and company_with_bin.company_signature:
            raw = company_with_bin.company_signature
            if isinstance(raw, bytes):
                signature_b64 = base64.b64encode(raw).decode('ascii')
            elif isinstance(raw, str) and len(raw) > 0:
                signature_b64 = raw

        # Recipient (vendor) information
        recipient_name = partner.name or ''
        recipient_address = self._format_address(partner)
        recipient_phone = partner.phone or partner.mobile or ''

        # Sender (company) information - By Order of
        company_name = company.name or ''
        company_address = self._format_address(company_partner)
        company_phone = company_partner.phone or company_partner.mobile or company.phone or ''
        company_email = company_partner.email or company.email or ''
        company_website = company.website or ''

        # Payment summary
        payment_method_name = self.payment_method_line_id.name if self.payment_method_line_id else ''
        payment_amount = self.amount
        payment_currency = self.currency_id

        # Related bill(s) total: sum of reconciled bills' amount_total (in payment currency) so report shows e.g. 800
        reconciled_bills_total = 0.0
        reconciled_bills_total_currency = payment_currency
        for inv in self.reconciled_bill_ids:
            reconciled_bills_total += inv.currency_id._convert(
                inv.amount_total, payment_currency, self.company_id, self.date
            )
        reconciled_bills_total_formatted = formatLang(
            self.env, reconciled_bills_total, currency_obj=reconciled_bills_total_currency
        ) if self.reconciled_bill_ids else ''

        # Bill details table: for each bill, one row (bill), then one row per payment/reversal, then "Due Amount for BILL/..."
        bill_table_rows = []
        for inv in self.reconciled_bill_ids:
            inv_currency = inv.currency_id
            # Bill row
            bill_table_rows.append({
                'row_type': 'bill',
                'date': inv.invoice_date,
                'date_formatted': format_date(self.env, inv.invoice_date) if inv.invoice_date else '',
                'number': inv.name,
                'reference': inv.ref or '',
                'amount': inv.amount_total,
                'currency': inv_currency,
                'amount_formatted': formatLang(self.env, inv.amount_total, currency_obj=inv_currency),
            })
            # Payment/reversal rows (partials)
            partials_list = inv._get_reconciled_invoices_partials()[0]
            for _partial, amount, other_aml in partials_list:
                pay_aml = other_aml
                pay_move = pay_aml.move_id
                amount_in_inv_currency = -amount  # payment reduces the due amount
                bill_table_rows.append({
                    'row_type': 'payment',
                    'date': pay_move.date,
                    'date_formatted': format_date(self.env, pay_move.date) if pay_move.date else '',
                    'number': pay_move.name,
                    'reference': pay_aml.payment_id.memo or inv.name or '',
                    'amount': amount_in_inv_currency,
                    'currency': inv_currency,
                    'amount_formatted': formatLang(self.env, amount_in_inv_currency, currency_obj=inv_currency),
                })
            # Due amount row
            bill_table_rows.append({
                'row_type': 'due',
                'date': None,
                'date_formatted': '',
                'number': 'Due Amount for %s' % (inv.name or ''),
                'reference': '',
                'amount': inv.amount_residual,
                'currency': inv_currency,
                'amount_formatted': formatLang(self.env, inv.amount_residual, currency_obj=inv_currency),
            })

        return {
            'company_signature': signature_b64,
            'recipient_name': recipient_name,
            'recipient_address': recipient_address,
            'recipient_phone': recipient_phone,
            'company_name': company_name,
            'company_address': company_address,
            'company_phone': company_phone,
            'company_email': company_email,
            'company_website': company_website,
            'payment_date': self.date,
            'payment_vendor': partner.name or '',
            'payment_method_name': payment_method_name,
            'payment_amount': payment_amount,
            'payment_currency': payment_currency,
            'payment_memo': self.memo or '',
            'reconciled_bills_total': reconciled_bills_total,
            'reconciled_bills_total_currency': reconciled_bills_total_currency,
            'reconciled_bills_total_formatted': reconciled_bills_total_formatted,
            'bill_table_rows': bill_table_rows,
        }
