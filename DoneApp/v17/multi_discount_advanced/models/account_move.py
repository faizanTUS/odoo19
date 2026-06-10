# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    show_multi_discount_in_pdf = fields.Boolean(
        string='Show Multi Discount in PDF Report',
        default=False,
        help='Display Multi Discount column in Invoice and Bill PDF reports'
    )

    def _prepare_product_base_line_for_taxes_computation(self, product_line):
        """Override to apply multi-discount before tax computation"""
        self.ensure_one()
        
        # Get the original price_unit
        original_price_unit = product_line.price_unit
        
        # Apply multi-discount to price_unit
        if product_line.multi_discount:
            # Multi-discount is a fixed amount per unit
            adjusted_price_unit = original_price_unit - product_line.multi_discount
        else:
            adjusted_price_unit = original_price_unit
        
        # Call parent method
        result = super()._prepare_product_base_line_for_taxes_computation(product_line)
        
        # Update the price_unit in the result to reflect multi-discount
        if 'price_unit' in result:
            result['price_unit'] = adjusted_price_unit
        
        return result


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

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

    @api.depends('price_unit', 'multi_discount', 'discount', 'quantity')
    def _compute_discount_amount(self):
        """Compute discount amount and discounted total amount"""
        for line in self:
            if not line.quantity:
                line.discount_amount = 0.0
                line.discounted_total_amount = 0.0
                continue

            # Apply multi-discount first (fixed amount per unit)
            price_after_multi_discount = line.price_unit - (line.multi_discount or 0.0)
            
            # Then apply percentage discount
            price_after_all_discounts = price_after_multi_discount * (1 - (line.discount or 0.0) / 100.0)
            
            # Calculate amounts
            line.discounted_total_amount = price_after_all_discounts * line.quantity
            total_discount = (line.price_unit - price_after_all_discounts) * line.quantity
            line.discount_amount = total_discount

