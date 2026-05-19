# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    purchase_order_ids = fields.Many2many(
        'purchase.order',
        string='Purchase Orders',
        compute='_compute_purchase_order_ids',
        copy=False,
        help='All RFQs and POs linked to this lead via Origin.',
    )
    purchase_quotation_count = fields.Integer(
        string='Purchase Quotations',
        compute='_compute_purchase_counts',
    )
    purchase_order_count = fields.Integer(
        string='Purchase Order Count',
        compute='_compute_purchase_counts',
    )
    purchase_order_amount_total = fields.Monetary(
        string='Purchase Orders Total',
        compute='_compute_purchase_counts',
        currency_field='company_currency',
    )
    purchase_line_ids = fields.One2many(
        'crm.lead.purchase.line',
        'lead_id',
        string='Requested products (for RFQ)',
        help='Products to pre-fill when creating a Purchase Quotation from this lead.',
    )
    required_by_date = fields.Date(
        string='Required by date',
        help='Desired delivery/required-by date; can be used as default on RFQs created from this lead.',
    )

    @api.depends_context('uid')
    def _compute_purchase_order_ids(self):
        for lead in self:
            if not lead.id:
                lead.purchase_order_ids = self.env['purchase.order']
                continue
            lead.purchase_order_ids = self.env['purchase.order'].search([
                ('opportunity_id', '=', lead.id),
            ])

    def _compute_purchase_counts(self):
        for lead in self:
            if not lead.id:
                lead.purchase_quotation_count = 0
                lead.purchase_order_count = 0
                lead.purchase_order_amount_total = 0.0
                continue
            orders = self.env['purchase.order'].search([('opportunity_id', '=', lead.id)])
            rfqs = orders.filtered(lambda o: o.state in ('draft', 'sent', 'to approve'))
            pos = orders.filtered(lambda o: o.state in ('purchase', 'done'))
            lead.purchase_quotation_count = len(rfqs)
            lead.purchase_order_count = len(pos)
            lead.purchase_order_amount_total = sum(pos.mapped('amount_total'))

    def action_new_purchase_quotation(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('New Purchase Quotation'),
            'res_model': 'crm.lead.purchase.quotation.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_lead_id': self.id,
                'active_model': 'crm.lead',
                'active_id': self.id,
            },
        }

    def action_view_purchase_quotations(self):
        self.ensure_one()
        orders = self.purchase_order_ids.filtered(lambda o: o.state in ('draft', 'sent', 'to approve'))
        return self._action_view_purchase_orders(orders, _('Purchase Quotations'))

    def action_view_purchase_orders(self):
        self.ensure_one()
        orders = self.purchase_order_ids.filtered(lambda o: o.state in ('purchase', 'done'))
        return self._action_view_purchase_orders(orders, _('Purchase Orders'))

    def _action_view_purchase_orders(self, orders, name):
        self.ensure_one()
        if not orders:
            return {'type': 'ir.actions.act_window_close'}
        if len(orders) == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': name,
                'res_model': 'purchase.order',
                'view_mode': 'form',
                'res_id': orders.id,
                'target': 'current',
            }
        return {
            'type': 'ir.actions.act_window',
            'name': name,
            'res_model': 'purchase.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', orders.ids)],
            'target': 'current',
        }
