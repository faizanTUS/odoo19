# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    _sql_constraints = [
        ('accountable_required_fields',
         "CHECK(display_type IS NULL OR (product_id IS NULL AND product_uom IS NULL))",
         "Missing required fields on accountable sale order line."),
        ('non_accountable_null_fields',
         "CHECK(display_type IS NULL OR (product_id IS NULL AND price_unit = 0 AND product_uom_qty = 0 AND product_uom IS NULL AND customer_lead = 0))",
         "Forbidden values on non-accountable sale order line"),
    ]
    def action_add_line_after(self):
        for line in self:
            order = line.order_id
            current_sequence = line.sequence
            later_lines = order.order_line.filtered(lambda l: l.sequence > current_sequence)
            for l in later_lines:
                l.sequence += 1
            order.write({
                'order_line': [(0, 0, {
                    'order_id': order.id,
                    'sequence': current_sequence + 1,
                    'product_id': False,
                    'name': 'New Line',
                    'product_uom_qty': 1,
                    'price_unit': 0.0,
                })]
            })
