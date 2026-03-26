# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _sale_out_of_stock_restriction_active(self):
        self.ensure_one()
        return self.env['ir.config_parameter'].sudo().get_param(
            'sale_out_of_stock_restriction.enabled'
        ) == 'True'

    def _sale_out_of_stock_restriction_base(self):
        base = self.env['ir.config_parameter'].sudo().get_param(
            'sale_out_of_stock_restriction.base', 'on_hand'
        )
        return base if base in ('on_hand', 'forecast') else 'on_hand'

    def _get_product_for_stock_check(self, product):
        self.ensure_one()
        if self.warehouse_id:
            return product.with_context(warehouse_id=self.warehouse_id.id)
        return product

    def _sale_out_of_stock_violation_lines(self):
        """Return sale.order.line records that exceed available qty (product UoM)."""
        self.ensure_one()
        if not self._sale_out_of_stock_restriction_active():
            return self.env['sale.order.line']

        base = self._sale_out_of_stock_restriction_base()
        bad_lines = self.env['sale.order.line']
        for line in self.order_line:
            if line.display_type or line.is_downpayment or not line.product_id:
                continue
            product = self._get_product_for_stock_check(line.product_id)
            if base == 'forecast':
                available = product.virtual_available
            else:
                available = product.qty_available
            qty_ordered = line.product_uom._compute_quantity(
                line.product_uom_qty,
                line.product_id.uom_id,
            )
            if float_compare(
                qty_ordered,
                available,
                precision_rounding=line.product_id.uom_id.rounding,
            ) == 1:
                bad_lines |= line
        return bad_lines

    def _sale_out_of_stock_restriction_message(self):
        self.ensure_one()
        lines = self._sale_out_of_stock_violation_lines()
        if not lines:
            return False
        base = self._sale_out_of_stock_restriction_base()
        if base == 'forecast':
            intro = _(
                'You cannot confirm this order because the following products are out of stock '
                'based on the forecast quantity:'
            )
        else:
            intro = _(
                'You cannot confirm this order because the following products are out of stock '
                'based on the quantity on hand:'
            )
        names = '\n'.join(f'- {line.product_id.display_name}' for line in lines)
        return f'{intro}\n\n{names}'

    def action_confirm(self):
        for order in self:
            msg = order._sale_out_of_stock_restriction_message()
            if msg:
                raise UserError(msg)
        return super().action_confirm()
