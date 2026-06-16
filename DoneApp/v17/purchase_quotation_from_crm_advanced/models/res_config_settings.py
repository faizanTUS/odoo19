# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools import str2bool


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    crm_rfq_vendor_action = fields.Selection(
        [
            ('create', 'Create a new vendor by default'),
            ('exist', 'Link to an existing vendor by default'),
        ],
        string='Default vendor choice when creating RFQ from Lead',
        default='exist',
    )

    # config_parameter = 'purchase_quotation_from_crm_advanced.vendor_action',
    crm_rfq_copy_expected_revenue = fields.Boolean(
        string='Copy Expected Revenue to RFQ notes',
        default=False,
    )
    # config_parameter = 'purchase_quotation_from_crm_advanced.copy_expected_revenue',
    crm_rfq_prefill_from_lead_products = fields.Boolean(
        string='Pre-fill RFQ lines from Lead requested products',
        default=False,
        help='If the lead has "Requested products" defined, use them as default lines in the new RFQ.'
    )
    # config_parameter = 'purchase_quotation_from_crm_advanced.prefill_from_lead_products',
    crm_rfq_required_by_days = fields.Integer(
        string='Default "Required by" (days from now)',
        default=7,
        help='Used to set Order Deadline / Expected Arrival when creating RFQ from Lead (0 = use today).'
    )

    # config_parameter='purchase_quotation_from_crm_advanced.required_by_days',
    @api.model
    def get_values(self):
        res = super().get_values()
        ir_config = self.env['ir.config_parameter'].sudo()

        res.update(
            crm_rfq_vendor_action=ir_config.get_param('purchase_quotation_from_crm_advanced.vendor_action'),
            crm_rfq_copy_expected_revenue=str2bool(
                ir_config.get_param('purchase_quotation_from_crm_advanced.copy_expected_revenue', 'False')
            ),
            crm_rfq_prefill_from_lead_products=str2bool(
                ir_config.get_param('purchase_quotation_from_crm_advanced.prefill_from_lead_products', 'False')),
            crm_rfq_required_by_days=int(
                ir_config.get_param('purchase_quotation_from_crm_advanced.required_by_days', 7)), )
        return res

    def set_values(self):
        super().set_values()
        ir_config = self.env['ir.config_parameter'].sudo()
        ir_config.set_param('purchase_quotation_from_crm_advanced.vendor_action', self.crm_rfq_vendor_action)

        ir_config.set_param('purchase_quotation_from_crm_advanced.copy_expected_revenue',
                            self.crm_rfq_copy_expected_revenue)

        ir_config.set_param('purchase_quotation_from_crm_advanced.prefill_from_lead_products',
                            self.crm_rfq_prefill_from_lead_products)

        ir_config.set_param('purchase_quotation_from_crm_advanced.required_by_days', self.crm_rfq_required_by_days or 0)
