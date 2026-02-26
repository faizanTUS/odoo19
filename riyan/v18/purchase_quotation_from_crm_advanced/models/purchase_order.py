# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    opportunity_id = fields.Many2one(
        'crm.lead',
        string='Lead/Opportunity',
        index=True,
        copy=False,
        help='CRM Lead or Opportunity from which this RFQ/PO was created.',
    )

    def action_view_lead(self):
        self.ensure_one()
        if not self.opportunity_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Lead/Opportunity'),
            'res_model': 'crm.lead',
            'view_mode': 'form',
            'res_id': self.opportunity_id.id,
            'target': 'current',
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('opportunity_id') and not vals.get('origin'):
                lead = self.env['crm.lead'].browse(vals['opportunity_id'])
                vals['origin'] = _('Lead/Opportunity: %s', lead.display_name)
        return super().create(vals_list)
