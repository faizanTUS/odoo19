# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CrmLeadPurchaseQuotationWizard(models.TransientModel):
    _name = 'crm.lead.purchase.quotation.wizard'
    _description = 'Create Purchase Quotation from CRM Lead'

    lead_id = fields.Many2one('crm.lead', string='Lead/Opportunity', required=True, readonly=True)

    action = fields.Selection([
        ('create', 'Create a new vendor'),
        ('exist', 'Link to an existing vendor'),
    ], string='Purchase Order Vendor', required=True)

    partner_id = fields.Many2one(
        'res.partner',
        string='Vendor',
        domain="[('company_id', 'in', [False, lead_company_id])]",
    )

    lead_company_id = fields.Many2one(
        'res.company',
        related='lead_id.company_id',
        readonly=True
    )

    # ---------------------------------------------------------
    # Helper: Get Settings Safely
    # ---------------------------------------------------------

    def _get_settings(self):
        """Fetch settings using res.config.settings"""
        settings = self.env['res.config.settings'].sudo().create({})
        return {
            'crm_rfq_vendor_action': settings.crm_rfq_vendor_action,
            'prefill': settings.crm_rfq_prefill_from_lead_products,
            'copy_revenue': settings.crm_rfq_copy_expected_revenue,
            'days': settings.crm_rfq_required_by_days,
        }

    # ---------------------------------------------------------
    # Default Get
    # ---------------------------------------------------------

    @api.model
    def default_get(self, fields_list):
        result = super().default_get(fields_list)

        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')

        if active_model != 'crm.lead' or not active_id:
            raise UserError(_('This wizard must be opened from a CRM Lead.'))

        lead = self.env['crm.lead'].browse(active_id)
        result['lead_id'] = lead.id

        settings = self._get_settings()

        # Default action from settings
        if 'action' in fields_list and not result.get('action'):
            vendor_action = settings['crm_rfq_vendor_action']
            result['action'] = vendor_action if vendor_action in ('create', 'exist') else 'exist'

        if ('partner_id' in fields_list and not result.get(
                'partner_id') and lead.partner_id and lead.partner_id.supplier_rank):
            result['partner_id'] = lead.partner_id.id

        return result

    # ---------------------------------------------------------
    # Main Action
    # ---------------------------------------------------------

    def action_create_purchase_quotation(self):
        self.ensure_one()

        lead = self.lead_id
        settings = self._get_settings()

        # Vendor logic
        if self.action == 'create':
            partner = self._create_vendor_from_lead(lead)
        else:
            if not self.partner_id:
                raise UserError(_('Please select a vendor.'))
            partner = self.partner_id

        # -------------------------------------------------
        # Build order lines (Prefill logic)
        # -------------------------------------------------

        order_lines = []
        if settings['prefill'] and lead.purchase_line_ids:
            for line in lead.purchase_line_ids:
                order_lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.display_name,
                    'product_qty': line.product_qty,
                    'product_uom': line.product_uom_id.id,
                    'price_unit': line.product_id.standard_price,
                    'date_planned': fields.Datetime.now(),
                }))

        # -------------------------------------------------
        # Deadline logic
        # -------------------------------------------------

        date_order = fields.Datetime.now()
        date_planned = date_order

        if lead.required_by_date:
            date_planned = fields.Datetime.to_datetime(lead.required_by_date)
        elif settings['days'] > 0:
            date_planned = date_order + timedelta(days=settings['days'])

        # -------------------------------------------------
        # Prepare Purchase Order values
        # -------------------------------------------------

        vals = {
            'partner_id': partner.id,
            'opportunity_id': lead.id,
            'order_line': order_lines,
            'date_order': date_order,
            'date_planned': date_planned,
        }

        # Copy revenue if enabled
        if settings['copy_revenue'] and lead.expected_revenue:
            vals['notes'] = _('Expected revenue (from Lead): %s') % lead.expected_revenue

        po = self.env['purchase.order'].create(vals)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Request for Quotation'),
            'res_model': 'purchase.order',
            'res_id': po.id,
            'view_mode': 'form',
            'target': 'current',
        }

    # ---------------------------------------------------------
    # Vendor Creation
    # ---------------------------------------------------------

    def _create_vendor_from_lead(self, lead):
        self.ensure_one()

        partner_vals = {
            'name': lead.partner_name or lead.contact_name or _('Vendor from Lead'),
            'email': lead.email_from,
            'phone': lead.phone or lead.mobile,
            'supplier_rank': 1,
        }

        if lead.company_id:
            partner_vals['company_id'] = lead.company_id.id

        return self.env['res.partner'].create(partner_vals)
