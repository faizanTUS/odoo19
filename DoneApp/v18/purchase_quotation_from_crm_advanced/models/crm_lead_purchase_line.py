# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CrmLeadPurchaseLine(models.Model):
    _name = 'crm.lead.purchase.line'
    _description = 'CRM Lead Requested Product (for Purchase)'

    lead_id = fields.Many2one('crm.lead', string='Lead/Opportunity', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    name = fields.Char(string='Description', related='product_id.name', readonly=False)
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', default=1.0)
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', related='product_id.uom_id', readonly=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.display_name
