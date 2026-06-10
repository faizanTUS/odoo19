# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    show_multi_discount_in_pdf = fields.Boolean(
        string='Show Multi Discount in PDF Report',
        default=False,
        help='Display Multi Discount column in Quotation and Sales Order PDF reports'
    )


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

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

    @api.depends('price_unit', 'multi_discount', 'discount', 'product_uom_qty')
    def _compute_discount_amount(self):
        """Compute discount amount and discounted total amount"""
        for line in self:
            if not line.product_uom_qty:
                line.discount_amount = 0.0
                line.discounted_total_amount = 0.0
                continue

            # Apply multi-discount first (fixed amount per unit)
            price_after_multi_discount = line.price_unit - (line.multi_discount or 0.0)
            
            # Then apply percentage discount
            price_after_all_discounts = price_after_multi_discount * (1 - (line.discount or 0.0) / 100.0)
            
            # Calculate amounts
            line.discounted_total_amount = price_after_all_discounts * line.product_uom_qty
            total_discount = (line.price_unit - price_after_all_discounts) * line.product_uom_qty
            line.discount_amount = total_discount

    def _prepare_base_line_for_taxes_computation(self, **kwargs):
        """Override to apply multi-discount before tax computation"""
        self.ensure_one()
        
        # Get the original price_unit
        original_price_unit = self.price_unit
        
        # Apply multi-discount to price_unit
        if self.multi_discount:
            # Multi-discount is a fixed amount per unit
            adjusted_price_unit = original_price_unit - self.multi_discount
        else:
            adjusted_price_unit = original_price_unit
        
        # Call parent method with adjusted price_unit
        result = super()._prepare_base_line_for_taxes_computation(**kwargs)
        
        # Update the price_unit in the result to reflect multi-discount
        if 'price_unit' in result:
            result['price_unit'] = adjusted_price_unit
        
        return result

