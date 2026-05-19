# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    show_multi_discount_in_pdf = fields.Boolean(
        string='Show Multi Discount in PDF Report',
        default=False,
        help='Display Multi Discount column in Quotation and Sales Order PDF reports'
    )

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    multi_discount = fields.Monetary(
        string='Multi Discount',
        default=0.0,
        help='Fixed amount discount applied before percentage discount'
    )
    discount_amount = fields.Monetary(
        string='Discount Amount',
        compute='_compute_discount_amount',
        store=True,
        help='Total discount amount (multi-discount + percentage discount)'
    )
    discounted_total_amount = fields.Monetary(
        string='Discounted Total Amount',
        compute='_compute_discount_amount',
        store=True,
        help='Total amount after applying multi-discount and percentage discount'
    )

    @api.depends('price_unit', 'multi_discount', 'product_qty')
    def _compute_discount_amount(self):
        """Compute discount amount and discounted total amount"""
        for line in self:
            if not line.product_qty:
                line.discount_amount = 0.0
                line.discounted_total_amount = 0.0
                continue

            # Apply multi-discount (fixed per unit)
            price_after_multi_discount = line.price_unit - (line.multi_discount or 0.0)

            # Calculate amounts
            line.discounted_total_amount = price_after_multi_discount * line.product_qty
            line.discount_amount = (line.price_unit * line.product_qty) - line.discounted_total_amount

    def _convert_to_tax_base_line_dict(self):
        """Override to apply multi-discount before tax computation"""
        self.ensure_one()
        res = super()._convert_to_tax_base_line_dict()
        # Adjust price_unit for taxes (apply fixed discount)
        if 'price_unit' in res:
            res['price_unit'] -= self.multi_discount or 0.0
            res['price_unit'] = max(res['price_unit'], 0.0)  # Avoid negative
        return res