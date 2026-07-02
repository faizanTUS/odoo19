# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MaterialRequisitionLine(models.Model):
    _name = 'material.requisition.line'
    _description = 'Material Requisition Line'

    requisition_id = fields.Many2one(
        'material.requisition',
        string='Material Requisition',
        required=True,
        ondelete='cascade',
        index=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        domain=[('type', 'in', ('product', 'consu'))],
        check_company=True,
    )
    description = fields.Char(string='Description')
    product_uom_id = fields.Many2one(
        'uom.uom',
        string='UoM',
        required=True,
        related='product_id.uom_id',
        readonly=False,
    )
    product_uom_category_id = fields.Many2one(
        related='product_id.uom_id.category_id',
    )
    required_qty = fields.Float(
        string='Required Quantity',
        digits='Product Unit of Measure',
        required=True,
        default=1.0,
    )
    purchase_price = fields.Float(
        string='Purchase Order Price',
        digits='Product Price',
    )
    requisition_action = fields.Selection(
        [
            ('purchase', 'Purchase Order'),
            ('internal', 'Internal Picking'),
        ],
        string='Requisition Action',
        required=True,
        default='internal',
        help='Purchase Order: generate RFQ/PO to vendor. Internal Picking: create internal transfer.',
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        check_company=True,
    )
    picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Picking Type',
        domain="[('code', '=', 'internal'), ('warehouse_id', '=', warehouse_id)]",
        check_company=True,
    )
    vendor_id = fields.Many2one(
        'res.partner',
        string='Vendor',
        domain="[('supplier_rank', '>', 0)]",
        check_company=True,
    )
    company_id = fields.Many2one(
        related='requisition_id.company_id',
        store=True,
    )
    picking_id = fields.Many2one(
        'stock.picking',
        string='Picking',
        readonly=True,
        copy=False,
    )
    purchase_order_line_id = fields.Many2one(
        'purchase.order.line',
        string='Purchase Order Line',
        readonly=True,
        copy=False,
    )
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        related='purchase_order_line_id.order_id',
        readonly=True,
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.display_name
            self.product_uom_id = self.product_id.uom_id
            if self.product_id.seller_ids:
                self.vendor_id = self.product_id.seller_ids[0].partner_id
                self.purchase_price = self.product_id.seller_ids[0].price

    @api.onchange('requisition_action')
    def _onchange_requisition_action(self):
        if self.requisition_action == 'purchase' and self.product_id and self.product_id.seller_ids:
            self.vendor_id = self.product_id.seller_ids[0].partner_id
            self.purchase_price = self.product_id.seller_ids[0].price

    @api.constrains('required_qty')
    def _check_line_config(self):
        for line in self:
            if line.required_qty <= 0:
                raise ValidationError(_('Required Quantity must be positive.'))
